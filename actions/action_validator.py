class ActionValidator:

    def validate(self, element):

        if element is None:
            return False

        # Must have a selector
        if not getattr(element, "selector", ""):
            return False

        # Hidden elements should not be used
        if hasattr(element, "visible"):

            if not element.visible:
                return False

        # Disabled elements should not be used
        if hasattr(element, "enabled"):

            if not element.enabled:
                return False

        return True

    def validate_with_reason(self, element):

        if element is None:

            return False, "Element not found."

        if not getattr(element, "selector", ""):

            return False, "Element has no selector."

        if hasattr(element, "visible"):

            if not element.visible:

                return False, "Element is not visible."

        if hasattr(element, "enabled"):

            if not element.enabled:

                return False, "Element is disabled."

        return True, "Validation successful."