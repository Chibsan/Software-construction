import argparse
import csv
import shlex
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path


NUTRIENTS = {
    "calories_kcal": ("Calories", "kcal"),
    "protein_g": ("Protein", "g"),
    "carbohydrate_g": ("Carbohydrate", "g"),
    "sugars_g": ("Sugars", "g"),
    "fat_g": ("Fat", "g"),
    "saturated_fat_g": ("Saturated fat", "g"),
    "fiber_g": ("Fiber", "g"),
    "sodium_mg": ("Sodium", "mg"),
}
RANKING_METRICS = {
    "carbohydrates": ("carbohydrate_g", "Carbohydrates", "g", False),
    "protein": ("protein_g", "Protein", "g", True),
    "fat": ("fat_g", "Fat", "g", False),
    "fiber": ("fiber_g", "Fiber", "g", True),
    "price": ("price_per_100g", "Price / 100 g", "", False),
}


@dataclass(frozen=True)
class Product:
    category: str
    name: str
    nutrients: dict[str, float | None]
    package_size_g: float
    product_price_eur: float
    price_per_100g: float


def load_products(csv_path: Path) -> list[Product]:
    required_columns = {
        "category",
        "name",
        "package_size_g",
        "product_price_eur",
        "price_per_100g",
        *NUTRIENTS,
    }
    products = []
    seen_names = set()

    with csv_path.open(encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        missing_columns = required_columns - set(reader.fieldnames or [])
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"CSV is missing required columns: {missing}")

        for line_number, row in enumerate(reader, start=2):
            category = (row.get("category") or "").strip()
            name = (row.get("name") or "").strip()
            if not category:
                raise ValueError(f"Row {line_number} has no product category")
            if not name:
                raise ValueError(f"Row {line_number} has no product name")
            if name.casefold() in seen_names:
                raise ValueError(f"Duplicate product name on row {line_number}: {name}")

            try:
                package_size = float(row["package_size_g"])
            except (TypeError, ValueError):
                raise ValueError(
                    f"Row {line_number} has an invalid value for package_size_g"
                ) from None
            if not isfinite(package_size) or package_size <= 0:
                raise ValueError(
                    f"Row {line_number} has an invalid package size; "
                    "it must be finite and greater than zero"
                )

            nutrients = {}
            for key in NUTRIENTS:
                raw_value = (row[key] or "").strip()
                if not raw_value:
                    nutrients[key] = None
                    continue
                try:
                    value = float(raw_value)
                except (TypeError, ValueError):
                    raise ValueError(
                        f"Row {line_number} has an invalid value for {key}"
                    ) from None
                if not isfinite(value) or value < 0:
                    raise ValueError(
                        f"Row {line_number} has an invalid value for {key}; "
                        "values must be finite and non-negative"
                    )
                nutrients[key] = value

            try:
                product_price = float(row["product_price_eur"])
            except (TypeError, ValueError):
                raise ValueError(
                    f"Row {line_number} has an invalid value for product_price_eur"
                ) from None
            if not isfinite(product_price) or product_price < 0:
                raise ValueError(
                    f"Row {line_number} has an invalid product price; "
                    "values must be finite and non-negative"
                )

            try:
                price = float(row["price_per_100g"])
            except (TypeError, ValueError):
                raise ValueError(
                    f"Row {line_number} has an invalid value for price_per_100g"
                ) from None
            if not isfinite(price) or price < 0:
                raise ValueError(
                    f"Row {line_number} has an invalid price; "
                    "values must be finite and non-negative"
                )

            seen_names.add(name.casefold())
            products.append(
                Product(
                    category=category,
                    name=name,
                    nutrients=nutrients,
                    package_size_g=package_size,
                    product_price_eur=product_price,
                    price_per_100g=price,
                )
            )

    if not products:
        raise ValueError("CSV contains no products")
    return products


def format_table(headers: list[str], rows: list[list[str]]) -> str:
    widths = [
        max(len(header), *(len(row[index]) for row in rows))
        for index, header in enumerate(headers)
    ]
    lines = [
        " | ".join(value.ljust(widths[index]) for index, value in enumerate(headers)),
        "-+-".join("-" * width for width in widths),
    ]
    lines.extend(
        " | ".join(value.ljust(widths[index]) for index, value in enumerate(row))
        for row in rows
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare product nutrition per 100 g using a CSV file."
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path(__file__).with_name("products.csv"),
        help="path to a product CSV file (default: products.csv)",
    )
    parser.add_argument(
        "--log",
        type=Path,
        default=Path(__file__).with_name("nutrition_history.log"),
        help="path for the prompt and answer history log",
    )
    commands = parser.add_subparsers(dest="command")
    commands.add_parser("interactive", help="choose a category, metric, and direction interactively")
    commands.add_parser("list", help="list products in the CSV")

    compare_parser = commands.add_parser("compare", help="compare selected products")
    compare_parser.add_argument("products", nargs="+", help="product names")

    rank_parser = commands.add_parser(
        "rank", help="rank products in a category across nutrition and price"
    )
    rank_parser.add_argument("category", help="product category, such as cheese")
    rank_parser.add_argument("priority", choices=RANKING_METRICS)
    rank_parser.add_argument("direction", choices=("most", "least"))
    return parser


def prompt_for_choice(prompt: str, choices: list[str]) -> str:
    options = ", ".join(choices)
    while True:
        answer = input(f"{prompt} ({options}): ").strip().casefold()
        if answer in choices:
            return answer
        print(f"Choose one of: {options}")


def prompt_for_numbered_choice(prompt: str, choices: list[str]) -> str:
    print(prompt)
    for number, choice in enumerate(choices, start=1):
        print(f"{number}. {choice}")

    while True:
        answer = input(f"Enter a number (1-{len(choices)}): ").strip()
        if answer.isdigit() and 1 <= int(answer) <= len(choices):
            return choices[int(answer) - 1]
        print(f"Enter a number from 1 to {len(choices)}.")


def get_metric_value(product: Product, metric_key: str) -> float | None:
    if metric_key == "price_per_100g":
        return product.price_per_100g
    return product.nutrients[metric_key]


def dense_ranks(
    products: list[Product], metric_key: str, highest_first: bool
) -> dict[str, int]:
    products_with_values = [
        (get_metric_value(product, metric_key), product)
        for product in products
        if get_metric_value(product, metric_key) is not None
    ]
    ordered = sorted(
        products_with_values,
        key=lambda item: (
            -item[0] if highest_first else item[0],
            item[1].name.casefold(),
        ),
    )
    ranks = {}
    previous_value = None
    current_rank = 0
    for value, product in ordered:
        if previous_value is None or value != previous_value:
            current_rank += 1
            previous_value = value
        ranks[product.name] = current_rank
    return ranks


def create_answer(args: argparse.Namespace) -> str:
    products = load_products(args.csv)

    if args.command == "list":
        return "\n".join(f"{product.category}: {product.name}" for product in products)

    if args.command == "compare":
        products_by_name = {product.name.casefold(): product for product in products}
        selected = []
        for name in args.products:
            product = products_by_name.get(name.casefold())
            if product is None:
                raise ValueError(f"Unknown product: {name}")
            selected.append(product)

        rows = []
        for key, (label, unit) in NUTRIENTS.items():
            values = [f"{product.nutrients[key]:g} {unit}" for product in selected]
            rows.append([label, *values])
        rows.append(
            [
                "Price / 100 g",
                *(f"{product.price_per_100g:.2f}" for product in selected),
            ]
        )
        rows.append(
            [
                "Product price / size",
                *(
                    f"€{product.product_price_eur:.2f}/{product.package_size_g:g}g"
                    for product in selected
                ),
            ]
        )
        return format_table(["Nutrient", *(product.name for product in selected)], rows)

    category_products = [
        product for product in products if product.category.casefold() == args.category.casefold()
    ]
    if not category_products:
        raise ValueError(f"No products found in category: {args.category}")

    priority_key, priority_label, _, _ = RANKING_METRICS[args.priority]
    priority_highest_first = args.direction == "most"
    overall_ranks = dense_ranks(
        category_products, priority_key, priority_highest_first
    )
    ranked = sorted(
        category_products,
        key=lambda product: (
            get_metric_value(product, priority_key) is None,
            (
                -get_metric_value(product, priority_key)
                if priority_highest_first
                else get_metric_value(product, priority_key)
            )
            if get_metric_value(product, priority_key) is not None
            else 0,
            product.name.casefold(),
        ),
    )

    metric_ranks = {}
    for metric, (key, _, _, preferred_highest) in RANKING_METRICS.items():
        highest_first = (
            priority_highest_first if metric == args.priority else preferred_highest
        )
        metric_ranks[metric] = dense_ranks(category_products, key, highest_first)

    ordered_metrics = [
        args.priority,
        *(metric for metric in RANKING_METRICS if metric != args.priority),
    ]
    rows = []
    for product in ranked:
        row = [str(overall_ranks.get(product.name, "NO-Rank")), product.name]
        for metric in ordered_metrics:
            key, _, unit, _ = RANKING_METRICS[metric]
            value = get_metric_value(product, key)
            if value is None:
                row.append("null (NO-Rank)")
                continue
            formatted_value = f"{value:.2f}" if metric == "price" else f"{value:g} {unit}"
            row.append(f"#{metric_ranks[metric][product.name]} ({formatted_value})")
        row.append(
            f"€{product.product_price_eur:.2f}/{product.package_size_g:g}g"
        )
        rows.append(row)

    headers = [
        "Priority rank",
        "Product",
        *(RANKING_METRICS[metric][1] for metric in ordered_metrics),
        "Product price / size",
    ]
    direction_label = "most" if priority_highest_first else "least"
    title = f"{category_products[0].category}: {direction_label} {priority_label}"
    return f"{title}\n{format_table(headers, rows)}"


def append_history(log_path: Path, prompt: str, answer: str) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(f"[{timestamp}]\nPrompt: {prompt}\nAnswer:\n{answer}\n\n")


def run_interactive(args: argparse.Namespace) -> int:
    try:
        products = load_products(args.csv)
        categories = sorted({product.category for product in products}, key=str.casefold)
        if len(categories) == 1:
            category = categories[0]
        else:
            category_choices = [item.casefold() for item in categories]
            selected_category = prompt_for_choice("Food category", category_choices)
            category = next(
                item for item in categories if item.casefold() == selected_category
            )

        ranking_choices = [
            f"{direction} {metric}"
            for metric in RANKING_METRICS
            for direction in ("most", "least")
        ]
        selected_ranking = prompt_for_numbered_choice("Choose ranking:", ranking_choices)
        direction, priority = selected_ranking.split(maxsplit=1)
        prompt = (
            f"interactive category={category} priority={priority} direction={direction}"
        )
        rank_args = argparse.Namespace(
            csv=args.csv,
            command="rank",
            category=category,
            priority=priority,
            direction=direction,
        )
        answer = create_answer(rank_args)
    except (OSError, ValueError, EOFError) as error:
        prompt = "interactive"
        answer = f"Error: {error}"
        exit_code = 1
    else:
        exit_code = 0

    print(answer)
    try:
        append_history(args.log, prompt, answer)
    except OSError as error:
        print(f"Could not write history log: {error}", file=sys.stderr)
        return 1
    return exit_code


def main(argv: list[str] | None = None) -> int:
    requested_args = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    args = parser.parse_args(requested_args)
    if args.command in (None, "interactive"):
        return run_interactive(args)

    prompt = shlex.join(["nutrition_compare.py", *requested_args])

    try:
        answer = create_answer(args)
    except (OSError, ValueError) as error:
        answer = f"Error: {error}"
        exit_code = 1
    else:
        exit_code = 0

    print(answer)
    try:
        append_history(args.log, prompt, answer)
    except OSError as error:
        print(f"Could not write history log: {error}", file=sys.stderr)
        return 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())