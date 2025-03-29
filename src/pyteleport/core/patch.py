import difflib
import os

import whatthepatch


class Patch:
    @staticmethod
    def diff(old_file, new_file, output_path):
        with open(old_file, "r") as f:
            old_text = f.read()

        with open(new_file, "r") as f:
            new_text = f.read()

        diff = difflib.unified_diff(
            old_text.splitlines(),
            new_text.splitlines(),
            fromfile=old_file,
            tofile=new_file,
        )

        with open(output_path, "w") as f:
            f.write("\n".join(diff))

    @staticmethod
    def apply(patch_file, target_file, is_save=True, is_remove_diff=False):
        with open(patch_file, "r") as f:
            patch_text = f.read()

        with open(target_file, "r") as f:
            target_text = f.read()

        diff = [x for x in whatthepatch.parse_patch(patch_text)]

        tzu = whatthepatch.apply_diff(diff[0], target_text)

        if is_save:
            result_txt = "\n".join(tzu)
            with open("sam.py", "w") as f:
                f.write(result_txt)

            if is_remove_diff:
                os.remove(patch_file)

    def apply_alpha(
        self, patch_file: str, is_save=True, is_remove_diff=False, is_diff_marker=False
    ):
        """apply method for alpha version"""
        with open(patch_file, "r") as f:
            patch_text = f.read()

        diff = [x for x in whatthepatch.parse_patch(patch_text)]
        self.result_txt = ""
        state = None
        for change in diff[0].changes:
            if change.old is not None and change.new is not None:
                state1 = None
            elif change.new is None:
                state1 = "SEARCH"
            elif change.old is None:
                state1 = "REPLACE"
            else:
                raise ValueError("Invalid change")
            if is_diff_marker:
                self._change_state_tag(state, state1)
            state = state1
            self.result_txt += change.line + "\n"
        if is_diff_marker:
            self._change_state_tag(state, None, end_tag=True)
        if is_save:
            # result_txt = "\n".join(tzu)
            with open("sam.py", "w") as f:
                f.write(self.result_txt)
            if is_remove_diff:
                os.remove(patch_file)

    def _change_state_tag(self, state_t0, state_t1, end_tag=False):
        if end_tag:
            if state_t0 == "SEARCH":
                self.change_state_tag("SEARCH", None, end_tag=False)
            elif state_t0 == "REPLACE":
                self.change_state_tag("REPLACE", None, end_tag=False)
            return

        if state_t0 == state_t1:
            return
        elif state_t0 is None and state_t1 == "SEARCH":
            self.result_txt += "<<<<<<< SEARCH\n"
        elif state_t0 == "SEARCH" and state_t1 == "REPLACE":
            self.result_txt += "=======\n"
        elif state_t0 == "REPLACE" and state_t1 is None:
            self.result_txt += ">>>>>>> REPLACE\n"
        else:
            if state_t0 is None and state_t1 == "REPLACE":
                self._change_state_tag(None, "SEARCH")
                self._change_state_tag("SEARCH", "REPLACE")
            elif state_t0 == "SEARCH" and state_t1 is None:
                self._change_state_tag("SEARCH", "REPLACE")
                self._change_state_tag("REPLACE", None)
            elif state_t0 == "REPLACE" and state_t1 == "SEARCH":
                self._change_state_tag("REPLACE", None)
                self._change_state_tag(None, "SEARCH")