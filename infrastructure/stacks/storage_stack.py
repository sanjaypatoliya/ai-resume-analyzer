import aws_cdk as cdk
from aws_cdk import aws_s3 as s3
from constructs import Construct


class StorageStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, env_name: str, **kwargs) -> None:  # type: ignore[no-untyped-def]
        super().__init__(scope, construct_id, **kwargs)

        self.bucket = s3.Bucket(
            self,
            "ResumeBucket",
            bucket_name=f"resume-parser-{env_name}-{self.account}",
            # Security: block all public access
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            # Encrypt at rest
            encryption=s3.BucketEncryption.S3_MANAGED,
            # Auto-cleanup for dev
            removal_policy=cdk.RemovalPolicy.DESTROY if env_name == "dev" else cdk.RemovalPolicy.RETAIN,
            auto_delete_objects=env_name == "dev",
            # Lifecycle rules — move old results to cheaper storage
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="archive-old-results",
                    prefix="results/",
                    transitions=[
                        s3.Transition(
                            storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                            transition_after=cdk.Duration.days(30),
                        )
                    ],
                ),
                s3.LifecycleRule(
                    id="expire-old-uploads",
                    prefix="uploads/",
                    expiration=cdk.Duration.days(7),  # Delete raw uploads after 7 days
                ),
            ],
            cors=[
                s3.CorsRule(
                    allowed_methods=[s3.HttpMethods.PUT, s3.HttpMethods.POST],
                    allowed_origins=["http://localhost:5173", "https://*"],
                    allowed_headers=["*"],
                    max_age=300,
                )
            ],
        )

        # Output bucket name for other stacks
        cdk.CfnOutput(self, "BucketName", value=self.bucket.bucket_name)
        cdk.CfnOutput(self, "BucketArn", value=self.bucket.bucket_arn)
