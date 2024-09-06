
from discord import Client, app_commands

class NRVCBot(Client):
    coms: list[app_commands.Command]
    
    def __init__(
        self,
        *args,
        coms: list[app_commands.Command],
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.tree = app_commands.CommandTree(self)
        self.coms = coms
        
    # 當機器人完成啟動
    async def on_ready(self):
        # await command.add.Add.setup(self)
        for com in self.coms:
            self.tree.add_command(com)
        slash = await self.tree.sync()
        print(f"目前登入身份 --> {self.user}")
        print(f"載入 {len(slash)} 個斜線指令")
    

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')
