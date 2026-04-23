import aws_cdk as cdk
from aws_cdk import (
    Duration,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
)
from constructs import Construct


class FrontendStack(cdk.Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        env_name: str,
        backend_url: str,
        **kwargs,  # type: ignore[no-untyped-def]
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # S3 bucket for React static files
        site_bucket = s3.Bucket(
            self,
            "SiteBucket",
            bucket_name=f"resume-parser-frontend-{env_name}-{self.account}",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # CloudFront Origin Access Control
        oac = cloudfront.S3OriginAccessControl(self, "OAC")

        # ALB origin for API routing (HTTP — CloudFront handles HTTPS termination)
        alb_domain = backend_url.replace("http://", "").replace("https://", "").rstrip("/")
        alb_origin = origins.HttpOrigin(
            alb_domain,
            protocol_policy=cloudfront.OriginProtocolPolicy.HTTP_ONLY,
            read_timeout=Duration.seconds(60),
            connection_timeout=Duration.seconds(10),
        )

        # CloudFront distribution
        distribution = cloudfront.Distribution(
            self,
            "Distribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(
                    site_bucket,
                    origin_access_control=oac,
                ),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
            ),
            additional_behaviors={
                "/api/v1/*": cloudfront.BehaviorOptions(
                    origin=alb_origin,
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL,
                    origin_request_policy=cloudfront.OriginRequestPolicy.ALL_VIEWER_EXCEPT_HOST_HEADER,
                ),
            },
            # SPA routing — send all 404s to index.html
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                ),
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                ),
            ],
            default_root_object="index.html",
            comment=f"Resume Parser Frontend - {env_name}",
        )

        # Deploy built React app to S3 and invalidate CloudFront cache
        s3_deployment.BucketDeployment(
            self,
            "DeployFrontend",
            sources=[s3_deployment.Source.asset("../frontend/dist")],
            destination_bucket=site_bucket,
            distribution=distribution,
            distribution_paths=["/*"],
        )

        self.cloudfront_url = f"https://{distribution.distribution_domain_name}"

        cdk.CfnOutput(self, "FrontendUrl", value=self.cloudfront_url)
        cdk.CfnOutput(self, "CloudFrontDomain", value=distribution.distribution_domain_name)
        cdk.CfnOutput(self, "BackendUrl", value=backend_url)
