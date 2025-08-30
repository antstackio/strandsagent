# Strands Agent Lambda Stack

A serverless application that deploys AI-powered agent Lambda functions using AWS CDK, featuring weather forecasting and database query capabilities through MCP (Model Context Protocol) handlers.

## Architecture Overview

This project deploys two Lambda functions:
- **Weather Agent Function**: Provides weather forecasting capabilities using AI agents
- **Query Agent Function**: Handles database queries with natural language processing

Both functions are built with Python 3.12, use AWS Bedrock for AI model invocations, and are deployed on ARM64 architecture for better performance and cost efficiency.

## Prerequisites

- Node.js (v18 or later)
- npm or yarn
- AWS CLI configured with appropriate credentials
- AWS CDK CLI (`npm install -g aws-cdk`)
- Python 3.12 (for local development)
- Docker (for building Lambda layers)

## Project Structure

```
strandsagent/
├── AgentLambdaStack.ts      # CDK stack definition
├── bin/                     # CDK app entry point
│   └── app.ts
├── lambda/                  # Lambda function source code
│   ├── query/
│   │   ├── mcp_handler.py
│   │   └── query_agent_handler.py
│   └── weather/
│       ├── mcp_handler.py
│       └── weather_agent_handler.py
├── packaging/               # Deployment packages
│   ├── dependencies.zip    # Lambda layer with dependencies
│   ├── query_app.zip      # Query function package
│   └── weather_app.zip    # Weather function package
├── cdk.json                # CDK configuration
├── package.json            # Node.js dependencies
└── requirements.txt        # Python dependencies
```

## Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# Required for Weather Function
OPENAI_KEY=your-openai-api-key

# Required for Query Function
DB_HOST=your-database-host
DB_PORT=5432
DB_NAME=your-database-name
DB_USER=your-database-user
DB_PASSWORD=your-database-password
```

### Environment Variable Details

- **OPENAI_KEY**: OpenAI API key for AI model access
- **DB_HOST**: PostgreSQL database hostname or IP address
- **DB_PORT**: Database port (default: 5432)
- **DB_NAME**: Name of the database to connect to
- **DB_USER**: Database username
- **DB_PASSWORD**: Database password

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd strandsagent
```

### 2. Install Node.js Dependencies

```bash
npm install
```

### 3. Install Python Dependencies (for local development)

```bash
pip install -r requirements.txt
```

### 4. Build Lambda Packages

Before deployment, ensure the Lambda deployment packages are built:

```bash
# Build dependencies layer
cd packaging
pip install -r ../requirements.txt -t _dependencies/
cd _dependencies && zip -r ../dependencies.zip . && cd ..

# Package Lambda functions (if not already packaged)
python bin/package_for_lambda.py
```

### 5. Configure AWS Credentials

Ensure your AWS CLI is configured:

```bash
aws configure
```

## Deployment Steps

### 1. Bootstrap CDK (first time only)

```bash
npx cdk bootstrap
```

### 2. Synthesize the CloudFormation Template

```bash
npx cdk synth
```

### 3. Deploy the Stack

```bash
npx cdk deploy
```

The deployment will:
- Create a Lambda layer with all Python dependencies
- Deploy the Weather Agent Lambda function
- Deploy the Query Agent Lambda function
- Set up IAM roles with necessary permissions for Bedrock access
- Configure environment variables for both functions

### 4. Verify Deployment

After successful deployment, you can verify the functions in the AWS Lambda console:
- Weather Agent Function: `WeatherAgentFunction`
- Query Agent Function: `QueryAgentFunction`

## Testing

### Local Testing

```bash
npm test
```

### Invoke Lambda Functions

Add the mcp to settings.json or to claude code

Make a natural language query about weather or about the database. The LLM will decide which agent to use.

## Development Commands

- `npm run watch` - Watch for TypeScript changes
- `npm run format` - Format code with Prettier
- `npx cdk diff` - Compare deployed stack with current state
- `npx cdk destroy` - Remove the stack from AWS

## IAM Permissions

Both Lambda functions are granted the following permissions:
- `bedrock:InvokeModel` - Invoke AI models
- `bedrock:InvokeModelWithResponseStream` - Stream model responses (if you are using bedrock models)

The Query function additionally requires VPC access if your database is in a private subnet.

## Monitoring and Logs

Lambda function logs are available in CloudWatch Logs:
- `/aws/lambda/WeatherAgentFunction`
- `/aws/lambda/QueryAgentFunction`

## Cost Considerations

- Lambda functions use ARM64 architecture for cost optimization
- Memory is set to 128MB (adjust based on your needs)
- Timeout settings:
  - Weather Function: 30 seconds
  - Query Function: 60 seconds

## Troubleshooting

### Common Issues

1. **Deployment fails with "Environment variable not found"**
   - Ensure all required environment variables are set in your `.env` file
   - Source the environment variables before deployment

2. **Lambda function times out**
   - Increase the timeout value in `AgentLambdaStack.ts`
   - Check network connectivity for database connections

3. **Bedrock access denied**
   - Verify your AWS account has access to Bedrock
   - Check the IAM role permissions

4. **Database connection fails**
   - Verify database credentials and network settings
   - Ensure Lambda has network access to the database (VPC configuration may be needed)

## Security Best Practices

- Store sensitive environment variables in AWS Secrets Manager or Parameter Store
- Use VPC endpoints for Bedrock access if Lambda is in a VPC
- Regularly rotate database credentials
- Enable CloudWatch Logs encryption
- Use least-privilege IAM policies

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Specify your license here]

## Support

For issues and questions, please open an issue in the GitHub repository.