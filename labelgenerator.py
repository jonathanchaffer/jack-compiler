class LabelGenerator:
    def __init__(self):
        self.labelNum = 0

    def nextLabel(self):
        label = 'L' + str(self.labelNum)
        self.labelNum += 1
        return label
