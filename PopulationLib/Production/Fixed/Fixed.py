

class Fixed:
    """
    Fixed production module
    """

    def __init__(self, xml_args):
        """
        Args:
            xml_args (lxml.etree._Element): production module specifications from project file tags
        """
        self.xml_args = xml_args

    def getTags(self, tags):
        """
        Return tags to search for in the project file
        Returns:
            dict
        """
        tags["optional"] += ["n_recruitment_per_step"]
        return tags

    def getNumberOfSeeds(self, plants):
        """
        Return the total number of seeds produced in the system, based on the number defined in the project file.
        Args:
            plants: - not used
        Returns:
            integer
        """
        return self.n_recruitment_per_step

