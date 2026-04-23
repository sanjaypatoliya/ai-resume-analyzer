import aws_cdk as cdk
from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_iam as iam,
    aws_ssm as ssm,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    aws_ecr_assets as ecr_assets,
)
from constructs import Construct


class BackendStack(cdk.Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        env_name: str,
        bucket: s3.Bucket,
        table: dynamodb.Table,
        **kwargs,  # type: ignore[no-untyped-def]
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC — 2 AZs, 1 NAT gateway to keep costs low
        vpc = ec2.Vpc(
            self,
            "Vpc",
            max_azs=2,
            nat_gateways=1,
        )

        # ECS Cluster
        cluster = ecs.Cluster(self, "Cluster", vpc=vpc, cluster_name=f"resume-parser-{env_name}")

        # IAM role for the Fargate task
        task_role = iam.Role(
            self,
            "TaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
        )

        # S3 permissions
        bucket.grant_read_write(task_role)

        # DynamoDB permissions
        table.grant_read_write_data(task_role)

        # Textract permissions
        task_role.add_to_policy(
            iam.PolicyStatement(
                actions=["textract:DetectDocumentText", "textract:StartDocumentTextDetection", "textract:GetDocumentTextDetection"],
                resources=["*"],
            )
        )

        # Bedrock permissions
        task_role.add_to_policy(
            iam.PolicyStatement(
                actions=["bedrock:InvokeModel"],
                resources=["*"],
            )
        )

        # SSM read permissions for secrets
        task_role.add_to_policy(
            iam.PolicyStatement(
                actions=["ssm:GetParameter", "ssm:GetParameters"],
                resources=[
                    f"arn:aws:ssm:{self.region}:{self.account}:parameter/resume-parser/{env_name}/*"
                ],
            )
        )

        # Read Anthropic API key from SSM (must be created manually before deploy)
        anthropic_key = ssm.StringParameter.from_secure_string_parameter_attributes(
            self,
            "AnthropicApiKey",
            parameter_name=f"/resume-parser/{env_name}/anthropic-api-key",
        )

        # Fargate service with ALB
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "FargateService",
            cluster=cluster,
            cpu=256,
            memory_limit_mib=512,
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_asset(
                    "../backend",
                    platform=ecr_assets.Platform.LINUX_AMD64,
                ),
                container_port=8000,
                task_role=task_role,
                environment={
                    "APP_ENV": env_name,
                    "AWS_REGION": self.region,
                    "S3_BUCKET": bucket.bucket_name,
                    "S3_PRESIGNED_URL_EXPIRY": "300",
                    "DYNAMODB_TABLE": table.table_name,
                    "ANTHROPIC_MODEL_ID": "claude-sonnet-4-6",
                },
                secrets={
                    "ANTHROPIC_API_KEY": ecs.Secret.from_ssm_parameter(anthropic_key),
                },
            ),
            public_load_balancer=True,
            service_name=f"resume-parser-backend-{env_name}",
        )

        # Health check
        fargate_service.target_group.configure_health_check(
            path="/health",
            healthy_http_codes="200",
        )

        # Scale down to 0 when not in use (manual control)
        fargate_service.service.auto_scale_task_count(
            max_capacity=2,
            min_capacity=1,
        )

        # Increase ALB idle timeout to match CloudFront max (60s) + buffer
        fargate_service.load_balancer.set_attribute("idle_timeout.timeout_seconds", "120")

        self.alb_dns = fargate_service.load_balancer.load_balancer_dns_name

        cdk.CfnOutput(self, "BackendUrl", value=f"http://{self.alb_dns}")
        cdk.CfnOutput(self, "ALBDnsName", value=self.alb_dns)
