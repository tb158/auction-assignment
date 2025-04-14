from munkres import Munkres

class ExtendedMunkres(Munkres):
    def get_internal_C(self):
        return self.C

    def get_marked_matrix(self):
        """Return the marked matrix."""
        return self.marked
