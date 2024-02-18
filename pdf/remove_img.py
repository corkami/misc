#!/usr/bin/env python3

# Ange Albertini 2024

from argparse import ArgumentParser
import pathlib
import fitz  # pyMuPDF

DESCRIPTION = "Selectively removes images from PDF files."
EPILOG = "example: %(prog)s ticket.pdf 0:1 1:1,2"


def remove_image(
        doc: fitz.Document,
        page_nb: int,
        img_nbs: list[int],
        no_placeholders: bool = False) -> fitz.Document:
    assert page_nb < doc.page_count
    page = doc[page_nb]
    page.clean_contents()
    itemlist = doc.get_page_images(page_nb)

    for img_nb in img_nbs:
        if (img_nb >= len(itemlist)):
            print(f"Image #{img_nb} not found on page {
                  page_nb}: {len(itemlist)} image(s) found.")
            return doc
        item = itemlist[img_nb]

        xref = item[0]
        rects = page.get_image_rects(xref)

        page.delete_image(xref)
        page.clean_contents()

        if not (no_placeholders):
            # TODO: draw placeholder underneath ?
            page.draw_rect(
                rects[0],
                color=(0.25, 0.25, 0.25),
                fill=(.9, .9, .9),
                width=1,
                dashes="[4] 0",
            )
    return doc


def get_args(arg: str) -> tuple[int, list[int]]:
    page_s, image_list = arg.split(":")
    page = int(page_s)
    images = [int(i) for i in image_list.split(',')]
    return page, images


def main() -> None:
    parser = ArgumentParser(description=DESCRIPTION, epilog=EPILOG)
    parser.add_argument("filename", type=str,
                        help="input filename")
    parser.add_argument("-o", "--output", type=str,
                        help="output filename")
    parser.add_argument("-n", "--no-placeholders", action='store_true',
                        help="Don't add placeholders in image positions")
    parser.add_argument("pages:images", type=str, nargs="+",
                        help='[<page>:<image>[,<image>]*]+ ')
    args = parser.parse_args()

    fn = args.filename
    no_placeholders = args.no_placeholders
    page_images = vars(args)["pages:images"]
    doc = fitz.open(fn)
    print(f"File: {fn}: {doc.page_count+1} page(s)")

    new_fn = args.output
    if new_fn is None:
        new_fn = f"{pathlib.PurePath(
            fn).stem}-noimg{pathlib.PurePath(fn).suffix}"

    for arg in page_images:
        page, images = get_args(arg)
        print(
            f"Removing in page {page} - image(s): {' '.join('%i' % i for i in images)}")
        doc = remove_image(doc, page, images, no_placeholders)

    print(f"Saving {new_fn}")
    doc.save(f"{new_fn}")


if __name__ == '__main__':
    main()
