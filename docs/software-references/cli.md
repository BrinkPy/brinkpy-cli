# CLI Dependencies and Citations

This page lists the top-level Python packages that Brinkpy CLI depends on. Use it if you need dependency-level software attribution in papers, reports, or technical notes.

If you are citing Brinkpy itself, cite the Zenodo software record: Carrasco, C. (2026). *Brinkpy CLI*. Zenodo. <https://doi.org/10.5281/zenodo.23752820>. If you need a fixed-version citation, use the version-specific Zenodo DOI for that release.

Only direct, top-level dependencies are listed — transitive packages installed automatically as dependencies of these libraries are not included.

## Packages with a Published Citation

The authors of these packages publish a preferred way to cite them, either a paper or a citation file. If you need to cite one of them, use the reference below:

- NumPy: Harris, C. R., Millman, K. J., van der Walt, S. J., et al. (2020). *Array programming with NumPy*. *Nature*, 585, 357-362. <https://doi.org/10.1038/s41586-020-2649-2>
- Matplotlib: Hunter, J. D. (2007). *Matplotlib: A 2D Graphics Environment*. *Computing in Science and Engineering*, 9(3), 90-95. <https://doi.org/10.1109/MCSE.2007.55>
- Typer: Ramírez, S. *Typer* (software). Citation metadata: <https://github.com/fastapi/typer/blob/master/CITATION.cff>
- Pydantic: Colvin, S., et al. *Pydantic Validation* (software). Citation metadata: <https://github.com/pydantic/pydantic/blob/main/CITATION.cff>

## Main CLI Libraries (Top-Level)

Brinkpy CLI needs every package below to run, including those listed above. To cite a package without a published citation, give its name, the version you used, and its project page, for example: *Requests* (version 2.34.2), <https://requests.readthedocs.io/>. Run `pip show <package>` to see the installed version.

- `typer`: https://typer.tiangolo.com/
- `rich`: https://rich.readthedocs.io/
- `requests`: https://requests.readthedocs.io/
- `numpy`: https://numpy.org/citing-numpy/
- `matplotlib`: https://matplotlib.org/stable/users/project/citing.html
- `pydantic`: https://docs.pydantic.dev/
- `typing_extensions`: https://pypi.org/project/typing_extensions/
- `filedialpy`: https://pypi.org/project/filedialpy/
- `platformdirs`: https://pypi.org/project/platformdirs/
- `python-dotenv`: https://pypi.org/project/python-dotenv/
- `PyJWT`: https://pyjwt.readthedocs.io/
- `pyyaml`: https://pyyaml.org/

## Tools Used to Build This Documentation

These packages build the Brinkpy documentation website. They are not installed with Brinkpy.

- `mkdocs`: https://www.mkdocs.org/
- `mkdocs-material`: https://squidfunk.github.io/mkdocs-material/
- `pymdown-extensions`: https://facelessuser.github.io/pymdown-extensions/
