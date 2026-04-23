import os
import aws_cdk as cdk
from stacks.storage_stack import StorageStack
from stacks.database_stack import DatabaseStack
from stacks.backend_stack import BackendStack
from stacks.frontend_stack import FrontendStack

app = cdk.App()

env_name = app.node.try_get_context("env") or "dev"

aws_env = cdk.Environment(
    account=app.node.try_get_context("account") or os.environ.get("CDK_DEFAULT_ACCOUNT"),
    region=app.node.try_get_context("region") or os.environ.get("CDK_DEFAULT_REGION") or "us-east-1",
)

# Stack 1 — S3 bucket for resume uploads
storage_stack = StorageStack(
    app,
    f"ResumeParser-Storage-{env_name}",
    env_name=env_name,
    env=aws_env,
)

# Stack 2 — DynamoDB table for analysis results
database_stack = DatabaseStack(
    app,
    f"ResumeParser-Database-{env_name}",
    env_name=env_name,
    env=aws_env,
)

# Stack 3 — ECS Fargate + ALB for FastAPI backend
backend_stack = BackendStack(
    app,
    f"ResumeParser-Backend-{env_name}",
    env_name=env_name,
    bucket=storage_stack.bucket,
    table=database_stack.table,
    env=aws_env,
)
backend_stack.add_dependency(storage_stack)
backend_stack.add_dependency(database_stack)

# Stack 4 — S3 + CloudFront for React frontend
frontend_stack = FrontendStack(
    app,
    f"ResumeParser-Frontend-{env_name}",
    env_name=env_name,
    backend_url=f"http://{backend_stack.alb_dns}",
    env=aws_env,
)
frontend_stack.add_dependency(backend_stack)

app.synth()
