;; compuTeX - Convert LaTeX -> SymPy -> evaluate -> LaTeX.
;; Copyright (C) 2023-2024 Soumendra Ganguly

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
    (call-process-region start end "computex.py" t t nil "-e" tex-code)))

(defun sgang-tex-computex-expand (start end)
  "convert LaTeX -> SymPy -> evaluate, expand -> LaTeX"
  (interactive "r")
  (let ((tex-code (buffer-substring start end)))
    (call-process-region start end "computex.py" t t nil "-e" "-E" tex-code)))

(defun sgang-tex-computex-factorize (start end)
  "convert LaTeX -> SymPy -> evaluate, factorize -> LaTeX"
  (interactive "r")
  (let ((tex-code (buffer-substring start end)))
    (call-process-region start end "computex.py" t t nil "-e" "-f" tex-code)))

(defun sgang-tex-computex-simplify (start end)
  "convert LaTeX -> SymPy -> evaluate, simplify -> LaTeX"
  (interactive "r")
  (let ((tex-code (buffer-substring start end)))
    (call-process-region start end "computex.py" t t nil "-e" "-s" tex-code)))

(defvar sgang-computex-map (make-sparse-keymap))
(define-key sgang-computex-map (kbd "z") 'sgang-tex-computex)
(define-key sgang-computex-map (kbd "e") 'sgang-tex-computex-expand)
(define-key sgang-computex-map (kbd "f") 'sgang-tex-computex-factorize)
(define-key sgang-computex-map (kbd "s") 'sgang-tex-computex-simplify)
