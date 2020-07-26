# pylint: disable=relative-beyond-top-level

"""

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.



    Important notice:

    This module is made by @myst33d, if you want
    to modify this module, please, leave this
    header, and respect the work of original author.

"""

import asyncio, urllib, json, secrets
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from .. import loader, utils

def register(cb): cb(PFPdMod())

class PFPdMod(loader.Module):
    strings = {"name": "Profile Picture Randomizer Daemon"}

    async def client_ready(self, client, db):
        self.client = client
        self.me = await self.client.get_me()
        self.running = False
        self.config = None
        self.timer = 0
        self.sleeptime = 0
        self.error = False

    async def pfpdconfigcmd(self, message):
        """Set a new JSON config URL for PFPd
        Usage: .pfpdconfig (link to your JSON file)"""
        args = utils.get_args(message)
        if args:
            self.config = args[0]
            await message.edit("New JSON config URL is set.")
        else: await message.edit("No JSON config URL is supplied.")

    async def pfpdstartcmd(self, message):
        """Start PFPd
        Usage: .pfpdstart (sleep time in seconds)
        
        P.S. If you unloaded this module without stopping PFPd daemon, delete the daemon message to stop the PFPd."""
        args = utils.get_args(message)
        if args:
            if self.running: await message.edit("PFPd is already running.")
            elif self.config:
                self.running = True
                self.error = False
                try: self.sleeptime = int(args[0])
                except:
                    self.running = False
                    self.error = True
                    self.sleeptime = 0
                    await message.edit("[PFPd] Failed to convert sleep time to integer.")
                while self.running:
                    await message.edit("[PFPd] Updating...")
                    try: pfpsjson = urllib.request.urlopen(self.config).read()
                    except:
                        self.running = False
                        self.error = True
                        self.sleeptime = 0
                        await message.edit("[PFPd] Invalid JSON config URL.\n(URL must contain https:// or http:// prefix)")
                        break
                    try: pfps = json.loads(pfpsjson)
                    except:
                        self.running = False
                        self.error = True
                        self.sleeptime = 0
                        await message.edit("[PFPd] Invalid JSON config file.")
                        break
                    try: photo = secrets.choice(pfps["pfps"])
                    except:
                        self.running = False
                        self.error = True
                        self.sleeptime = 0
                        await message.edit("[PFPd] Invalid JSON config file.\nMake sure \"pfps\" key is a list and it contains atleast one photo.")
                        break
                    try: pfpfile = urllib.request.urlopen(photo)
                    except:
                        self.running = False
                        self.error = True
                        self.sleeptime = 0
                        await message.edit("[PFPd] Invalid photo URL: {}\n(URL must contain https:// or http:// prefix)".format(photo))
                        break
                    try:
                        await self.client(UploadProfilePhotoRequest(await self.client.upload_file(pfpfile)))
                        await self.client(DeletePhotosRequest(await self.client.get_profile_photos(self.me.username, offset=1)))
                        await message.edit("[PFPd] Updated successfully.")
                        self.timer = self.sleeptime
                        while self.timer:
                            if self.running:
                                await asyncio.sleep(1)
                                self.timer -= 1
                            else: break
                    except:
                        await message.edit("[PFPd] Flood timeout, waiting 200 seconds...")
                        self.timer = 200
                        while self.timer:
                            if self.running:
                                await asyncio.sleep(1)
                                self.timer -= 1
                            else: break
                if not self.error: await message.edit("Stopped.")
            else: await message.edit("No JSON config URL is set.")
        else: await message.edit("No sleep time supplied.")

    async def pfpdstopcmd(self, message):
        """Stop PFPd
        Usage: .pfpdstop"""
        if self.running:
            await message.edit("Stopping...")
            self.running = False
            await asyncio.sleep(2)
            self.timer = 0
            self.sleeptime = 0
            await message.edit("PFPd stopped.")
        else: await message.edit("PFPd is not running.")

    async def pfpdstatuscmd(self, message):
        """Get PFPd status
        Usage: .pfpdstatus"""
        await message.edit("=== PFPd status ===\nJSON config URL: {}\nSleep time: {} seconds\nNext update: {} seconds\nPFPd running: {}\nError: {}".format(self.config, self.sleeptime, self.timer, self.running, self.error))
