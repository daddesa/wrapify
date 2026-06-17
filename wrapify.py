import pandas as pd
import json
import glob
import os

### CONFIGURATION SWITCHES
# 0 = default only | 1 = show side-by-side comparison
SHOW_ARTISTS_MINUTES = 0  # if set to 1 adds "Top 5 Artists by Minutes" next to Plays
SHOW_SONGS_PLAYS = 0      # if set to 1 adds "Top 5 Songs by Plays" next to Minutes

### CUTOFF SETTINGS
# default cutoff date for any year not specified below (MM, DD)
# as explained in the README.MD, i found the 15th of November to be a good compromise result-wise
DEFAULT_CUTOFF_MONTH = 11
DEFAULT_CUTOFF_DAY = 15

# Custom cutoff dates for specific years (Format: YYYY: "MM-DD")
# if you want to cut the analysis to specific dates, add them here
# EXAMPLE: { 2023: "11-28", 2024: "12-05" }
CUSTOM_CUTOFFS = {}

# a stream counts if played for at least 30 seconds.
MINIMUM_PLAY_MS = 30000 

# remember to drop your .json file(s) in the root of your colab folder
FILE_PATTERN = '/Streaming_History_Audio_*.json'

def format_string(text, max_len=32):
    """Truncates strings to maintain strict table alignment."""
    if len(text) > max_len:
        return text[:max_len-3] + "..."
    return text

def main():
    print("================================================================================")
    print("SPOTIFY WRAPPED REPLICA")
    print("================================================================================\n")

    file_paths = glob.glob(FILE_PATTERN)

    if not file_paths:
        print(f"Error: No files found at '{FILE_PATTERN}'.")
        return
    
    data = []
    for file in file_paths:
        with open(file, 'r', encoding='utf-8') as f:
            data.extend(json.load(f))

    df = pd.DataFrame(data)

    
    df['ts'] = pd.to_datetime(df['ts'])
    df['year'] = df['ts'].dt.year
    df['date'] = df['ts'].dt.date
    df = df[df['master_metadata_track_name'].notna()].copy()
    df['minutes_played'] = df['ms_played'] / 60000
    df_valid = df[df['ms_played'] >= MINIMUM_PLAY_MS].copy()


    years = sorted(df_valid['year'].dropna().unique())

    for year in years:
        print(f"{'='*85}")
        
        # check for user-defined custom cutoffs
        if year in CUSTOM_CUTOFFS:
            custom_date_str = f"{int(year)}-{CUSTOM_CUTOFFS[year]}"
            cutoff_date = pd.to_datetime(custom_date_str).date()
            print(f"YEAR: {int(year)} (Using custom cutoff: {cutoff_date})")
        else:
            cutoff_date = pd.to_datetime(f"{int(year)}-{DEFAULT_CUTOFF_MONTH:02d}-{DEFAULT_CUTOFF_DAY:02d}").date()
            print(f"YEAR: {int(year)} (Using default cutoff: {cutoff_date})")
            
        print(f"{'='*85}")

        df_year = df_valid[(df_valid['year'] == year) & (df_valid['date'] <= cutoff_date)]

        if df_year.empty:
            print("  No data available for this year.\n")
            continue

        ### ARTISTS (sorted by default by plays)
        plays_art_df = df_year.groupby('master_metadata_album_artist_name').size().reset_index(name='plays')
        top_5_art_plays = plays_art_df.sort_values(by=['plays', 'master_metadata_album_artist_name'], ascending=[False, True]).head(5).reset_index(drop=True)

        print("\n--- TOP 5 ARTISTS ---")
        if SHOW_ARTISTS_MINUTES == 1:
            mins_art_df = df_year.groupby('master_metadata_album_artist_name')['minutes_played'].sum().reset_index(name='minutes')
            top_5_art_mins = mins_art_df.sort_values(by=['minutes', 'master_metadata_album_artist_name'], ascending=[False, True]).head(5).reset_index(drop=True)
            
            print(f"{'RANK':<5} | {'BY PLAY COUNT':<36} | {'BY MINUTES PLAYED':<36}")
            print("-" * 85)
            for i in range(5):
                # Plays
                if i < len(top_5_art_plays):
                    art_p = format_string(str(top_5_art_plays.loc[i, 'master_metadata_album_artist_name']), 24)
                    val_p = top_5_art_plays.loc[i, 'plays']
                    str_p = f"{art_p} ({val_p})"
                else:
                    str_p = ""
                # Minutes
                if i < len(top_5_art_mins):
                    art_m = format_string(str(top_5_art_mins.loc[i, 'master_metadata_album_artist_name']), 24)
                    val_m = top_5_art_mins.loc[i, 'minutes']
                    str_m = f"{art_m} ({val_m:.1f}m)"
                else:
                    str_m = ""
                print(f"{i+1:<5} | {str_p:<36} | {str_m:<36}")
        else:
            print(f"{'RANK':<5} | {'BY PLAY COUNT'}")
            print("-" * 85)
            for i in range(len(top_5_art_plays)):
                art_p = format_string(str(top_5_art_plays.loc[i, 'master_metadata_album_artist_name']), 60)
                val_p = top_5_art_plays.loc[i, 'plays']
                print(f"{i+1:<5} | {art_p} ({val_p} plays)")

        ### SONGS (sorted by default by minutes)
        mins_song_df = df_year.groupby(['master_metadata_track_name', 'master_metadata_album_artist_name'])['minutes_played'].sum().reset_index(name='minutes')
        top_5_song_mins = mins_song_df.sort_values(by=['minutes', 'master_metadata_track_name'], ascending=[False, True]).head(5).reset_index(drop=True)

        print("\n--- TOP 5 SONGS ---")
        if SHOW_SONGS_PLAYS == 1:
            plays_song_df = df_year.groupby(['master_metadata_track_name', 'master_metadata_album_artist_name']).size().reset_index(name='plays')
            top_5_song_plays = plays_song_df.sort_values(by=['plays', 'master_metadata_track_name'], ascending=[False, True]).head(5).reset_index(drop=True)

            print(f"{'RANK':<5} | {'BY MINUTES PLAYED':<36} | {'BY PLAY COUNT':<36}")
            print("-" * 85)
            for i in range(5):
                # Minutes
                if i < len(top_5_song_mins):
                    trk_m = str(top_5_song_mins.loc[i, 'master_metadata_track_name'])
                    art_m = str(top_5_song_mins.loc[i, 'master_metadata_album_artist_name'])
                    val_m = top_5_song_mins.loc[i, 'minutes']
                    str_m = f"{format_string(f'{trk_m} - {art_m}', 24)} ({val_m:.1f}m)"
                else:
                    str_m = ""
                # Plays
                if i < len(top_5_song_plays):
                    trk_p = str(top_5_song_plays.loc[i, 'master_metadata_track_name'])
                    art_p = str(top_5_song_plays.loc[i, 'master_metadata_album_artist_name'])
                    val_p = top_5_song_plays.loc[i, 'plays']
                    str_p = f"{format_string(f'{trk_p} - {art_p}', 24)} ({val_p})"
                else:
                    str_p = ""
                print(f"{i+1:<5} | {str_m:<36} | {str_p:<36}")
        else:
            print(f"{'RANK':<5} | {'BY MINUTES PLAYED'}")
            print("-" * 85)
            for i in range(len(top_5_song_mins)):
                trk_m = str(top_5_song_mins.loc[i, 'master_metadata_track_name'])
                art_m = str(top_5_song_mins.loc[i, 'master_metadata_album_artist_name'])
                val_m = top_5_song_mins.loc[i, 'minutes']
                full_str = format_string(f"'{trk_m}' - {art_m}", 60)
                print(f"{i+1:<5} | {full_str} ({val_m:.1f} min)")
        
        print("\n")

if __name__ == "__main__":
    main()
