class DOMInspector:

    def inspect(self, locator):

        def safe(method, default=""):

            try:
                value = method()

                return value if value else default

            except Exception:
                return default

        def safe_attr(name):

            try:

                value = locator.get_attribute(name)

                return value if value else ""

            except Exception:

                return ""

        metadata = {

            "text": safe(locator.inner_text),

            "value": safe(locator.input_value),

            "placeholder": safe_attr("placeholder"),

            "aria_label": safe_attr("aria-label"),

            "title": safe_attr("title"),

            "element_id": safe_attr("id"),

            "classes": safe_attr("class"),

            "name": safe_attr("name"),

            "data_testid": safe_attr("data-testid"),

            "visible": locator.is_visible(),

            "enabled": locator.is_enabled()

        }

        return metadata