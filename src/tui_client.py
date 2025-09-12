"""TUI client for the geodata chatbot using textual."""

import asyncio
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Header, Footer, Input, RichLog, Static
from textual.binding import Binding
from langgraph_sdk import get_client

class ChatApp(App):
    """A TUI chat application."""
    
    CSS = """
    Screen {
        layout: vertical;
    }
    
    #chat-log {
        height: 1fr;
        border: solid $accent;
        margin: 1;
        padding: 1;
    }
    
    #input-container {
        dock: bottom;
        height: 3;
        margin: 1;
    }
    
    #chat-input {
        dock: left;
        width: 1fr;
    }
    
    #send-button {
        dock: right;
        width: 8;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("enter", "send_message", "Send", show=False),
    ]
    
    def __init__(self):
        super().__init__()
        self.client = get_client(url="http://localhost:2024")
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield RichLog(id="chat-log", markup=True)
        with Horizontal(id="input-container"):
            yield Input(
                placeholder="Type your message here...",
                id="chat-input"
            )
            yield Button("Send", id="send-button", variant="primary")
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when app starts."""
        chat_log = self.query_one("#chat-log", RichLog)
        chat_log.write("[bold green]Geodata Chatbot TUI[/bold green]")
        chat_log.write("[dim]Type your message and press Enter to chat[/dim]")
        
        # Focus the input field
        self.query_one("#chat-input", Input).focus()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "send-button":
            self.send_message()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle input submission (Enter key)."""
        self.send_message()
    
    def action_send_message(self) -> None:
        """Action to send a message."""
        self.send_message()
    
    def send_message(self) -> None:
        """Send the current message."""
        input_widget = self.query_one("#chat-input", Input)
        message = input_widget.value.strip()
        
        if not message:
            return
        
        # Clear input
        input_widget.value = ""
        
        # Add user message to chat log
        chat_log = self.query_one("#chat-log", RichLog)
        chat_log.write(f"[bold blue]You:[/bold blue] {message}")
        
        # Send message to chatbot (run async)
        asyncio.create_task(self.get_bot_response(message))
    
    async def get_bot_response(self, user_message: str) -> None:
        """Get response from the chatbot."""
        chat_log = self.query_one("#chat-log", RichLog)
        
        try:
            response_text = ""
            
            async for chunk in self.client.runs.stream(
                None,  # Threadless run
                "agent",  # Name of assistant
                input={
                    "messages": [{
                        "role": "human",
                        "content": user_message,
                    }],
                },
                stream_mode="messages-tuple"
            ):
                if chunk.event == "messages":
                    message_chunk, metadata = chunk.data
                    if message_chunk["content"]:
                        response_text += message_chunk["content"]
                        # Clear and rewrite from assistant line
                        chat_log.clear()
                        chat_log.write("[bold green]Geodata Chatbot TUI[/bold green]")
                        chat_log.write("[dim]Type your message and press Enter to chat[/dim]")
                        chat_log.write(f"[bold blue]You:[/bold blue] {user_message}")
                        chat_log.write(f"[bold green]Assistant:[/bold green] {response_text}")
            
            
        except Exception as e:
            chat_log.write(f"[bold red]Error:[/bold red] {str(e)}")

def main():
    """Run the TUI application."""
    app = ChatApp()
    app.run()

if __name__ == "__main__":
    main()