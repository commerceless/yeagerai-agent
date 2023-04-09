import os
from typing import Any

from git import Repo, Actor
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentFinish

from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate, LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)


class GitLocalRepoCallbackHandler(BaseCallbackHandler):
    """Callback Handler that creates a local git repo and commits changes."""

    def __init__(self, username: str, session_path: str) -> None:
        """Initialize callback handler."""
        super().__init__()
        self.username = username
        self.session_path = session_path
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        # Check if the directory contains a Git repository
        try:
            self.repo = Repo(self.session_path)
            print("Found existing Git repository at:", self.session_path)
        except:
            # If the directory does not contain a Git repository, create a new one
            os.makedirs(self.session_path, exist_ok=True)
            self.repo = Repo.init(self.session_path)
            print("Created new Git repository at:", self.session_path)

        self.committer = Actor(self.username, f"{self.username}@example.com")

    def _get_gpt_commit_message(self, repo: Repo) -> str:
        """
        Call the GPT API to get a commit message that explains the differences.
        """
        # Get the differences
        diff_output = repo.git.diff(repo.head.commit.tree)

        # Create a prompt template
        prompt_template = "Explain the following changes in a Git commit message:\n\n{diff_output}\n\nCommit message:"

        # Initialize ChatOpenAI with API key and model name
        chat = ChatOpenAI(
            openai_api_key=self.openai_api_key, model_name="gpt-3.5-turbo"
        )

        # Create a PromptTemplate instance with the read template
        master_prompt = PromptTemplate(
            input_variables=["diff_output"],
            template=prompt_template,
        )

        # Create a HumanMessagePromptTemplate instance with the master prompt
        human_message_prompt = HumanMessagePromptTemplate(prompt=master_prompt)
        chat_prompt = ChatPromptTemplate.from_messages([human_message_prompt])

        # Create an LLMChain instance and run the command
        chain = LLMChain(llm=chat, prompt=chat_prompt)

        commit_message = chain.run(diff_output=diff_output)

        return commit_message

    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> None:
        """Commit changes when an agent finishes its execution."""
        self.repo.git.add(A=True)

        if self.repo.is_dirty():
            commit_message = self._get_gpt_commit_message(self.repo)
            self.repo.index.commit(
                commit_message, author=self.committer, committer=self.committer
            )

    def on_agent_action(self):
        pass

    def on_chain_end(self):
        pass

    def on_chain_error(self):
        pass

    def on_chain_start(self):
        pass

    def on_llm_end(self):
        pass

    def on_llm_error(self):
        pass

    def on_llm_new_token(self):
        pass

    def on_llm_start(self):
        pass

    def on_text(self):
        pass

    def on_tool_end(self):
        pass

    def on_tool_error(self):
        pass

    def on_tool_start(self):
        pass