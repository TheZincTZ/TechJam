"""
Small synthetic catalog for local smoke-testing before you plug in the
real frozen 50k-item Amazon Clothing_Shoes_and_Jewelry catalog from the
participant kit. Replace `load_sample_catalog` usage with a real loader
(e.g. `load_catalog_from_json(path)`) once you have the kit downloaded.
"""
from __future__ import annotations
from typing import List
from models import Product


def load_sample_catalog() -> List[Product]:
    return [
        Product("B001", "Men's Running Sneakers", "shoes", price=59.99, brand="Nova",
                attributes={"color": "black", "size": "9"}, description="Lightweight breathable running shoe."),
        Product("B002", "Women's Casual Sneakers", "shoes", price=45.00, brand="Nova",
                attributes={"color": "white", "size": "8"}, description="Everyday casual canvas sneaker."),
        Product("B003", "Leather Ankle Boots", "boots", price=89.50, brand="Trekline",
                attributes={"color": "brown", "size": "9"}, description="Waterproof leather ankle boot."),
        Product("B004", "Gold Plated Necklace", "jewelry", price=25.00, brand="Lumeire",
                attributes={"color": "gold"}, description="Delicate chain necklace, gift-ready box."),
        Product("B005", "Silver Hoop Earrings", "jewelry", price=18.00, brand="Lumeire",
                attributes={"color": "silver"}, description="Classic hoop earrings for everyday wear."),
        Product("B006", "Men's Denim Jacket", "jacket", price=75.00, brand="Urban Forge",
                attributes={"color": "blue"}, description="Classic fit denim jacket, casual layering piece."),
        Product("B007", "Women's Summer Dress", "dress", price=39.99, brand="Solstice",
                attributes={"color": "yellow"}, description="Floral print dress, lightweight cotton."),
        Product("B008", "Slim Fit Jeans", "jeans", price=49.99, brand="Urban Forge",
                attributes={"color": "navy", "size": "32"}, description="Stretch denim slim fit jeans."),
        Product("B009", "Men's Formal Dress Shoes", "shoes", price=99.00, brand="Trekline",
                attributes={"color": "black", "size": "10"}, description="Oxford leather formal shoe."),
        Product("B010", "Kids Velcro Sneakers", "shoes", price=29.99, brand="Nova",
                attributes={"color": "red", "size": "2"}, description="Easy velcro sneaker for kids."),
        Product("B011", "Wrist Watch Classic", "jewelry", price=120.00, brand="Chronel",
                attributes={"color": "silver"}, description="Analog wrist watch, stainless steel band."),
        Product("B012", "Canvas Tote Bag", "bag", price=22.00, brand="Solstice",
                attributes={"color": "beige"}, description="Everyday canvas tote, roomy interior."),
        Product("B013", "Women's Hiking Boots", "boots", price=110.00, brand="Trekline",
                attributes={"color": "green", "size": "8"}, description="Rugged sole hiking boot, ankle support."),
        Product("B014", "Men's Polo Shirt", "shirt", price=32.00, brand="Urban Forge",
                attributes={"color": "white"}, description="Cotton pique polo, classic collar."),
        Product("B015", "Statement Pendant Necklace", "jewelry", price=34.00, brand="Lumeire",
                attributes={"color": "gold"}, description="Bold pendant necklace, gift for her."),
    ]
