from automation.platforms.intron_platform import IntronPlatform


class PlatformFactory:

    def create(self, name, browser):

        name = name.lower()

        if name == "intron":

            return IntronPlatform(browser)

        raise ValueError(
            f"Unknown platform: {name}"
        )