# Wrapify: An Open-Source Spotify Wrapped Analyzer

**Wrapify** allows you to process your raw Spotify JSON data directly, offering precise control over the analysis timeframe and full transparency into the metrics used to rank your listening habits.

## Key Features

* **Empirically Tuned Defaults:** Based on a strict double-check against 7 years of official Spotify Wrapped data, the script defaults to ranking **Artists by Play Count** and **Songs by Minutes Played**, as these metrics yield the most historically accurate reflection of the official results.
* **Dual Metric Toggles:** Built-in switches allow you to enable side-by-side comparisons (plays vs. minutes) to see how track length and skipping habits skew your personal rankings.
* **Customizable Timeframes:** Override the default cutoff dates (see below) to match exact historical tracking periods.

## Getting Your Data

1. Go to your Spotify Account settings on a web browser.
2. Navigate to **Privacy -> Download your data**.
3. Request your **Extended streaming history**. *(Note: Spotify warns this may take up to 30 days since it contains your entire lifetime history. In practice, it usually arrives within a few hours).*
4. Once downloaded, extract the `.zip` file. You will find multiple files named `Streaming_History_Audio_X.json`.

## Usage

This script was primarily designed to be run in a cloud notebook environment like Google Colab, but can easily be run locally.

### Option A: Running on Google Colab
1. Open a new Google Colab notebook and paste the code from `wrapify.py`.
2. Upload all your `Streaming_History_Audio_*.json` files directly to the root directory of the Colab environment.
3. Leave the file pattern as is: `FILE_PATTERN = '/Streaming_History_Audio_*.json'`
4. Run the cell.

### Option B: Running Locally
1. Place your `.json` files in the exact same directory as the `wrapped_analyzer.py` script.
2. **Important:** Open the script and remove the forward slash `/` from the file pattern variable so it looks like this:
   `FILE_PATTERN = 'Streaming_History_Audio_*.json'`
3. This tool requires Python 3 and the `pandas` library.
   To install the required dependency locally, run:
   `pip install pandas`
4. Run the script via terminal: `python wrapped_analyzer.py`

## Configuration

You can customize the script's behavior by modifying the variables at the top of the file:

* `SHOW_ARTISTS_MINUTES` / `SHOW_SONGS_PLAYS`: Set to `1` to enable the dual-metric tables, or `0` for the empirically accurate default view.
* `DEFAULT_CUTOFF_MONTH` / `DEFAULT_CUTOFF_DAY`: Through testing, **November 15th** has proven to be the most statistically consistent fallback cutoff date across multiple years.
* `CUSTOM_CUTOFFS`: A dictionary allowing you to set exact cutoff dates for specific years (e.g., `{ 2023: "11-28" }`) if you know exactly when Spotify stopped tracking.

## Known Limitations

When comparing Wrapify's output to your official Wrapped, you may notice slight discrepancies in artist rankings, specifically for artists involved in frequent collaborations or producer tags. 

Wrapify groups data using the `master_metadata_album_artist_name` string exactly as it appears in the raw JSON. Spotify's internal algorithm, however, splits joint ventures (e.g., "Artist A & Artist B") and featured verses, crediting both artists individually. Without complex regex string-splitting, solo minutes for highly collaborative artists will naturally appear lower in this raw analysis than in the official graphics.

## Future Improvements

* **1:1 Cutoff Matching:** Reverse-engineering the exact day Spotify halted tracking for every single historical year. Currently, the custom dictionary allows manual input, but a fully automated historical mapping is planned.
* **Collaboration Tag Parsing:** Properly handling collaboration names, featured artists, and producer tags.
