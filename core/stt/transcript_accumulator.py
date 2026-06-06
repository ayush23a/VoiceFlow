class TranscriptAccumulator:

    def __init__(self):
        self.transcript = ""

    def update(self, text):

        text = text.strip()

        if not text:
            return self.transcript

        if not self.transcript:
            self.transcript = text
            return self.transcript

        prev_words = self.transcript.split()
        curr_words = text.split()

        max_overlap = 0

        max_check = min(
            len(prev_words),
            len(curr_words)
        )
            
        for overlap in range(
            max_check,
            0,
            -1
        ):

            if (
                prev_words[-overlap:]
                ==
                curr_words[:overlap]
            ):
                max_overlap = overlap
                break

        new_words = curr_words[max_overlap:]

        if new_words:
            self.transcript += (
                " "
                + " ".join(new_words)
            )

        return self.transcript