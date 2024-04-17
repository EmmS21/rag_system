import { ChatOpenAI } from "langchain/chat_models/openai";
import { PromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, BasePromptTemplate } from "langchain/prompts";
import { ConversationChain } from "langchain/chains";
import fs from 'fs';
// import { dev } from '$app/environment';

const apiKey = process.env.VITE_OPENAI_API_KEY;

const model = new ChatOpenAI({ openAIApiKey: apiKey });


/**
 * @param {fs.PathOrFileDescriptor} filePath
 */
export async function generateUnitTestSuggestions(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const scriptSections = parseSvelteComponents(content);

    const systemPrompt = SystemMessagePromptTemplate.fromTemplate(
        "You are an AI assistant specialized in generating comprehensive unit test suggestions for Svelte components based on their code. Your task is to analyze the provided code snippets and provide detailed suggestions for relevant unit tests that should be written to ensure thorough testing coverage."
    );    
    
    for (const section of scriptSections) {
        const prompt = buildReActPrompt(section);
        const humanPrompt = new HumanMessagePromptTemplate({
            template: prompt
          });
          const fullPrompt = new PromptTemplate({
            inputVariables: [],
            template: "{system_message}\n\n{user_message}",
            partialVariables: {
              system_message: systemPrompt.toString(),
              user_message: humanPrompt.toString()
            }
          });  
        const chain = new ConversationChain({ llm: model, prompt: fullPrompt, outputKey: 'result' });
        // console.log('chain***', chain)

      // Call the chain to generate the response
      const response = await chain.call({ input: humanPrompt.toString() });
    //   const response = await chain.call({ input: '' });
      console.log(`Generated Unit Test Suggestions for ${section.type}:\n`, response.text);
    }
  } catch (error) {
    console.error('Error generating unit test suggestions:', error);
    throw error;
  }
}

/**
 * @param {string} content
 */
function parseSvelteComponents(content) {
  /** @type {{ type: string; code: any; }[]} */
  const sections = [];
  const functionRegex = /function\s+(\w+)\s*\(.*?\)\s*{.*?}/gs;
  const reactiveStatements = /\$:\s+(.*?);/gs;
  const eventHandlers = /on:\w+\s*=\s*"(.*?)"/gs;

  content.match(functionRegex)?.forEach(match => {
    sections.push({ type: 'function', code: match });
  });

  content.match(reactiveStatements)?.forEach(match => {
    sections.push({ type: 'reactive', code: match });
  });

  content.match(eventHandlers)?.forEach(match => {
    sections.push({ type: 'event-handler', code: match });
  });

  return sections;
}

/**
 * @param {{ type: any; code: any; }} section
 */
function buildReActPrompt(section) {
  switch (section.type) {
    case 'function':
      return `Describe unit tests for a JavaScript function: ${section.code}`;
    case 'reactive':
      return `Describe unit tests for a Svelte reactive statement: ${section.code}`;
    case 'event-handler':
      return `Describe unit tests for a Svelte event handler: ${section.code}`;
    default:
      return `Describe unit tests for the code: ${section.code}`;
  }
}

// Assuming your Svelte file is located at 'src/routes/+page.svelte'
generateUnitTestSuggestions('../../routes/+page.svelte').catch(console.error);
// /src/routes/+page.svelte