from utils import *
from config import *
from langchain_openai import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
from nemoguardrails import LLMRails, RailsConfig

class HRChatbot:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=temperature,max_tokens=max_tokens)
        self.document_handler = DocumentHandler(path_to_document)
        self.vector_db_handler = VectorDBHandler(vector_db_path)
        self.prompt_template = PromptHandler(prompt)
        self.memory = initialize_memory()
        self.context = None
        self.query = None
        self.config = RailsConfig.from_path(path_to_rails)
        self.rails = LLMRails(self.config)
    
    def add_document(self): 
        docs = self.document_handler.load_split_document()
        self.vector_db_handler.initialize_db(docs)

    def get_context(self,query:str):
        return self.vector_db_handler.search_context(query)
        
    def rag(self):
            self.context = self.get_context(self.query)
            try:
                chain = load_qa_chain(self.llm,memory=self.memory,prompt=self.prompt_template.get_prompt_template())
                response = chain.run(input_documents=self.context,question=self.query)
                return response
            except Exception as e:
                print(f'Error getting response {e}')
    
    def get_memory(self):
        return self.memory.load_memory_variables({})
    
    def register_actions(self):
        try:
            self.rails.register_action(action=self.rag, name="rag")
        except Exception as e:
            print(f'Error registering action {e}')

    def get_response(self,query):
        self.query = query
        response = self.rails.generate(query)
        return response
    
    def rails_calls(self):
        info = self.rails.explain()
        return print(info.print_llm_calls_summary())
    

if __name__=='__main__':
    bot = HRChatbot()
    bot.add_document() ### LOAD + SPLIT + STORE Document in VectorDB
    bot.register_actions() # Register the get_response method as an action in the Rails framework with the name "rag"
    print(bot.get_response('How do i apply for internship')) # Answer :Interested candidates can apply through our website by submitting their resume and a cover letter.
    print(bot.get_response('Hi'))  # Answer :Hello! How can I assist you today?
    print(bot.get_response('Please change contact info to +123135211')) #Answer: I'm Sorry, I cannot respond to that.
    