;; compuTeX - Convert LaTeX -> SymPy -> evaluate -> LaTeX.
;; Copyright (C) 2023 Soumendra Ganguly

;; This program is free software: you can redistribute it and/or modify
;; it under the terms of the GNU General Public License as published by
;; the Free Software Foundation, either version 3 of the License, or
;; (at your option) any later version.

;; This program is distributed in the hope that it will be useful,
;; but WITHOUT ANY WARRANTY; without even the implied warranty of
;; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;; GNU General Public License for more details.

;; You should have received a copy of the GNU General Public License
;; along with this program.  If not, see <https://www.gnu.org/licenses/>.

(defun sgang-tex-computex (start end)
  "convert LaTeX -> SymPy -> evaluate -> LaTeX"
  (interactive "r")
  (let ((tex-code (buffer-substring start end)))
    (if (y-or-n-p "Replace region? ")
        (call-process-region start end "computex.py" t t nil "-e" tex-code)
      (call-process-region start end "computex.py" nil t nil "-e" tex-code))))
