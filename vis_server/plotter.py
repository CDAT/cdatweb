import vcs


class PlotManager(object):
    def __init__(self, canvas):
        self.canvas = canvas

        self.dp = None
        self.dp_ind = 0
        self._gm = None
        self._vars = None
        self._template = None

    def can_plot(self):
        return self.dp is not None or (self._template is not None and self._vars is not None and self._gm is not None)

    def gm(self):
        return self._gm

    def set_gm(self, gm):
        # check gm vs vars
        self._gm = gm
        if self.can_plot():
            self.plot()

    graphics_method = property(gm, set_gm)

    def get_vars(self):
        return self._vars

    def set_vars(self, v):
        try:
            self._vars = (v[0], v[1])
        except TypeError:
            self._vars = (v, None)
        except IndexError:
            self._vars = (v[0], None)

        if self.can_plot():
            self.plot()

    variables = property(get_vars, set_vars)

    def templ(self):
        return self._template

    def set_templ(self, template):
        # Check if gm supports templates
        self._template = template
        if self.can_plot():
            self.plot()

    template = property(templ, set_templ)

    def plot(self):
        if self.variables is None:
            raise ValueError("No variables specified")
        if self.graphics_method is None:
            raise ValueError("No graphics method specified")
        # Check if gm supports templates
        if self.template is None:
            raise ValueError("No template specified")

        if self.dp is not None:
            if self.dp.name not in self.canvas.display_names:
                self.dp = vcs.elements["display"][self.canvas.display_names[self.dp_ind]]
            # Set the slabs appropriately
            self.dp.array[0] = self.variables[0]
            self.dp.array[1] = self.variables[1]

            # Update the template
            self.dp._template_origin = self.template.name

            # Update the graphics method
            self.dp.g_name = self.graphics_method.name
            self.dp.g_type = vcs.graphicsmethodtype(self.graphics_method)

            ind = self.canvas.display_names.index(self.dp.name)

            # Update the canvas
            self.canvas.update()

            self.dp = vcs.elements["display"][self.canvas.display_names[ind]]

        else:
            args = []
            for var in self.variables:
                if var is not None:
                    args.append(var)
            args.append(self.template.name)
            args.append(vcs.graphicsmethodtype(self.graphics_method))
            args.append(self.graphics_method.name)
            self.dp = self.canvas.plot(*args, ratio="autot")
            self.dp_ind = self.canvas.display_names.index(self.dp.name)
