from munkres import Munkres

class ExtendedMunkres(Munkres):
    def get_internal_C(self):
        return self.C

    def get_marked_matrix(self):
        """Return the marked matrix."""
        return self.marked
    
    # 0の位置を総出力するメソッドはない
    # 参考 step2~3で割り当てている
