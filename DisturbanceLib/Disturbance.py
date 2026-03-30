#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import importlib


class Disturbance:
    """
    Manage selected disturbance concepts (e.g. Hurricane, Lightning)
    and apply them sequentially at each timestep.
    """

    def __init__(self, args, project=None):
        """
        Args:
            args (lxml.etree._Element): <disturbance> node from project file
            project: MangaProject object (optional)
        """
        self.disturbance_concepts = []
        self.disturbance_concept_names = []
        self.iniDisturbanceConcept(args, project)

    def iniDisturbanceConcept(self, args, project):
        """
        Initialize disturbance concepts from XML configuration.
        Supports child-tag style: <Hurricane>...</Hurricane>.
        A shared <domain> block can be defined once at <disturbance> level.
        Args:
            args (lxml.etree._Element): <disturbance> node
            project: MangaProject object (optional)
        """
        # Read shared domain if defined at disturbance level
        domain_node = args.find("domain")

        for child in args:
            tag = getattr(child, "tag", None)
            if not isinstance(tag, str):
                continue
            name = tag.strip()
            if not name or name == "domain":
                continue
            module_dir = "DisturbanceLib."
            concept = self._importModule(name, module_dir, child, project,
                                         domain_node)
            self.disturbance_concepts.append(concept)
            self.disturbance_concept_names.append(name)
            print("Disturbance: {}.".format(name))

        if not self.disturbance_concepts:
            raise KeyError(
                "Missing disturbance concept in project file. "
                "Specify e.g. <Hurricane>...</Hurricane> inside <disturbance>.")

    def _importModule(self, module_name, module_dir, prj_args, project,
                      domain_node=None):
        """
        Dynamically load a disturbance concept module.
        Args:
            module_name (string): name of the module (e.g. 'Hurricane')
            module_dir (string): path prefix (e.g. 'DisturbanceLib.')
            prj_args (lxml.etree._Element): module XML node
            project: MangaProject object
            domain_node: shared <domain> XML node (optional)
        Returns:
            class instance
        """
        module_full_path = module_dir + module_name + "." + module_name
        try:
            module = importlib.import_module(module_full_path)
            my_class = getattr(module, module_name)
            my_instance = my_class(prj_args, project=project)
        except ModuleNotFoundError:
            print("ModuleNotFoundError: No module named '" + module_full_path + "'")
            print("Make sure the module exists and spelling is correct.")
            exit()
        # Apply shared domain if concept has no own domain defined
        if domain_node is not None:
            for attr in ["x_1", "x_2", "y_1", "y_2"]:
                if getattr(my_instance, attr, None) is None:
                    val = domain_node.findtext(attr)
                    if val is not None:
                        setattr(my_instance, attr, float(val.strip()))
        return my_instance

    def getDisturbanceConceptNames(self):
        """
        Return list of loaded disturbance concept names.
        Returns:
            list of strings
        """
        return self.disturbance_concept_names

    def apply(self, t_ini, t_end, plants):
        """
        Apply all disturbance concepts for a timestep.
        Args:
            t_ini (float): start time of the timestep
            t_end (float): end time of the timestep
            plants (list): collection of plant objects
        """
        if not plants or not self.disturbance_concepts:
            return
        for concept in self.disturbance_concepts:
            concept.apply(t_ini=t_ini, t_end=t_end, plants=plants)
