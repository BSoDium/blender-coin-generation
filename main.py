def main():
    # by default the all workflow is computed, and all results are cached.
    # you can bypass results by adding args to the CLI (like --force download)
    # or by setting it into the settings.py file. (it will first look at the setting file, then at args)
    # there is a default_settings.py inside the libs folder with all the default params
    # a step can be skipped (--skip-download for example) so downloaded images can be removed from the
    # cache, without re-downloading it again

    # parse arguments
    # parse default settings
    # parse settings
    # apply arguments

    # 1. launch downloading
    # 2. launch coin finding
    # 3. launch texutre generator
    # 4. launch blender picture generation
    # 5. launch export into Hugging Face

    # each step is run as a Step, a there can be a progression sending to
    # this object, in order to have great progress bar (in console, or in web html
    # page if it is run in a server for example)

    # download_step = Step()
    # download_step.name = "Download"
    # download_step.description = "Download"

    # if not data.is_scraped:
    #   download_step.run("Scrape")
    # if not data.is_cached:
    #   download_step.run("Download")

    # download_step.onProgress(update_progressbar)

    pass


if __name__ == "__main__":
    main()
