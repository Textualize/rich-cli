from textual import events
from textual.app import App
from textual.widgets import ScrollView


class PagerApp(App):
    """App to scroll renderable"""

    def __init__(
        self,
        *args,
        content=None,
        **kwargs,
    ) -> None:
        self.content = content
        super().__init__(*args, **kwargs)

    async def on_load(self, event: events.Load) -> None:
        await self.bind("q", "quit", "Quit")

    async def on_mount(self, event: events.Mount) -> None:
        self.body = body = ScrollView()
        await self.view.dock(body)
        await body.focus()
        await body.update(self.content)
