from collections import deque
from re import match
from yt_dlp import YoutubeDL
from discord import FFmpegOpusAudio, Embed, Color
from youtubesearchpython import VideosSearch
from datetime import timedelta

from Song import Song


class AudioController():

    ffmpeg_options = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }

    def __init__(self):
        current_song = None
        self.playlist = deque()
    
    def queue(self, url):
        self.playlist.append(url)
    
    def remove(self, index):
        playlist_as_list = list(self.playlist)
        playlist_as_list.pop(index)
        self.playlist = deque(playlist_as_list)

    def play_next(self, ctx):
        if len(self.playlist) > 0:
            nextSong = self.playlist.pop()

            ctx.voice_client.play(FFmpegOpusAudio(nextSong.base_url, executable='ffmpeg', **self.ffmpeg_options), after=lambda e: self.play_next(ctx))
            self.current_song = nextSong.title
        else:
            self.current_song = None

    async def play(self, ctx, query):
        if not match(r'http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]*)(&(amp;)?‌​[\w\?‌​=]*)?', query):
            videosSearch = VideosSearch(query, limit=1)
            url = videosSearch.result()['result'][0]['link']
            query = url
            
        downloader = YoutubeDL(
            {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '128',
                }]
            }
        )
        info = downloader.extract_info(query, download=False)
        duration = str(timedelta(seconds=info.get('duration')))[2:]
        nextSong = Song(title=info.get('title'), base_url=info.get('url'), duration=duration, yt_link=query)

        self.queue(nextSong)
        if ctx.voice_client.is_playing():
            embed = Embed(title="Added to Queue", description=f"[{nextSong.title}]({nextSong.yt_link})", color=Color.random())
            await ctx.send(embed=embed)
        else:
            self.play_next(ctx)
            embed = Embed(title="Now Playing", description=f"[{nextSong.title}]({nextSong.yt_link})", color=Color.random())
            await ctx.send(embed=embed)

    def get_queue_embed(self):
        embed = Embed(title="Queue", color=Color.random())
        for i, song in enumerate(self.playlist):
            embed.add_field(name=f'{i+1}. {song.title}', value=f'\tDuration: {song.duration}', inline=False)
        return embed