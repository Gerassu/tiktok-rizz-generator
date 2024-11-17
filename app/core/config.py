#@todo Config Management


#add config settings for video processor

class video_settings():
    placeholder_video: str #add which placeholder 
    codec: str
    width: int
    height: int


#add config settings for Claude prompt

class claude_settings():
    #add claude api settings
    api_key: str # from configs.ini 
    model_id: str # use haijìku 3.5 or sonnet 3.0

#add config settings for ElevenLabs voice info

class elabs_settings():
    api_key: str # from configs.ini 
    model_id: str # use Multilingual v2, Multilingual v1, English v1 and Turbo v2, Turbo v2.5

    #add claude api settings


#add config settings for possible speech to text / text from claude 
# subtitles (font size, color, formatting, extra)
