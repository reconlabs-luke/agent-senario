import { CognitoIdentityProviderClient, InitiateAuthCommand, AuthFlowType } from '@aws-sdk/client-cognito-identity-provider';
import dotenv from 'dotenv';

dotenv.config();

interface InvocationOutput {
    result_prompt: string
    result_image: string | null
}

async function authenticateAndGetTokens(username: string, passwordPlain: string, clientId: string) {
    const client = new CognitoIdentityProviderClient({ region });

    try {
        const command = new InitiateAuthCommand({
            AuthFlow: AuthFlowType.USER_PASSWORD_AUTH,
            ClientId: clientId,
            AuthParameters: {
                USERNAME: username,
                PASSWORD: passwordPlain,
            },
        });

        const response = await client.send(command);
        const authenticationResult = response.AuthenticationResult;

        if (authenticationResult) {
            const accessToken = authenticationResult.AccessToken;
            const idToken = authenticationResult.IdToken;
            const refreshToken = authenticationResult.RefreshToken;
            
            return { accessToken, idToken, refreshToken };
        }
        return null;
    } catch (error) {
        console.error('Error during authentication:', error);
        return null;
    }
}

async function request(url: string, accessToken: string, prompts: Array<string>): Promise<InvocationOutput> {
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            'prompts': prompts,
        }),
    });
    return response.json() as Promise<InvocationOutput>;
}

const username = process.env?.COGNITO_USERNAME || "reconlabs";
const passwordPlain = process.env?.COGNITO_PASSWORD || "Reconlabs1234!@";
const clientId = process.env?.COGNITO_CLIENT_ID || "2fp3n6g1tibkn1dt1laljf4n7j";
const region = process.env?.AWS_REGION || "us-east-1";

async function main() {
    const tokens = await authenticateAndGetTokens(username, passwordPlain, clientId);
    const version = "v1"
    const url = `https://bedrock-agentcore.${region}.amazonaws.com/runtimes/arn%3Aaws%3Abedrock-agentcore%3Aus-east-1%3A207637378596%3Aruntime%2Fgroup_to_text_agent-WtTLz83hBj/invocations?qualifier=${version}`
    const response = await request(url, tokens?.accessToken || "", [
        "Warm terracotta and mustard color palette for accent wall", 
        "Natural oak flooring with linen curtains", 
        "Minimalist Scandinavian interior with natural light"
    ]); 

    console.log(response);
}

main();
