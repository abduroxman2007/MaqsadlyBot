from telegram.ext import Application
from config import BOT_TOKEN
from handlers.start import start_handler
from handlers.check import check_handler
from handlers.join_request import join_request_handler
from handlers.admin import admin_handler, admin_stats_handler, admin_export_handler, broadcast_conv, admin_stats_command_handler, admin_export_command_handler, admin_channels_handler, admin_channels_command_handler
from data.db import init_db

import nest_asyncio
nest_asyncio.apply()

async def main():
    await init_db()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(start_handler)
    app.add_handler(check_handler)
    app.add_handler(join_request_handler)
    app.add_handler(broadcast_conv)
    app.add_handler(admin_handler)
    app.add_handler(admin_stats_handler)
    app.add_handler(admin_stats_command_handler)
    app.add_handler(admin_export_handler)
    app.add_handler(admin_export_command_handler)
    app.add_handler(admin_channels_handler)
    app.add_handler(admin_channels_command_handler)
    await app.run_polling()

if __name__ == '__main__':
    import asyncio
    # asyncio.run(main())
    # Instead, run the main function directly if it's not async:
    import sys
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main()) 