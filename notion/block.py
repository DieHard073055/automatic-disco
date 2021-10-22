class Block:
    @staticmethod
    def heading_1(title):
        return dict(
            object="block",
            type="heading_2",
            heading_2=dict(text=[dict(type="text", text=dict(content=title))]),
        )

    @staticmethod
    def text_block(text):
        return dict(
            object="block",
            type="paragraph",
            paragraph=dict(text=[dict(type="text", text=dict(content=text))]),
        )
