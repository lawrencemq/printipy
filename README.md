# PrintiPy
The Printify API for Python


## documentation - to do

## create product

Example:
Even though the data below has more information than the API needs, the extraneous data will be filtered out automatically and the call will be sucessfully made.
```python
new_product_data = {
        "title": "Testy McTestFace",
        "description": "suc test. wow!",
        "tags": [
            "Home & Living",
            "Paper",
            "Sustainable",
            "Greeting Card",
            "Postcard",
            "Card",
            "Post cards",
            "Postcards",
            "Made in USA"
        ],
        "blueprint_id": 1094,
        "print_provider_id": 228,
        "variants": [
            {
                "id": 81870,
                "price": 999,
                "is_enabled": True,
            },
            {
                "id": 81871,
                "price": 2499,
                "is_enabled": True,
            },
            {
                "id": 81872,
                "price": 4399,
                "is_enabled": True,
            },
            {
                "id": 81873,
                "price": 5599,
                "is_enabled": True,
            },
        ],
        "print_areas": [
            {
                "variant_ids": [
                    81810,
                    81811,
                    81812,
                    81813,
                    81822,
                    81823,
                    81824,
                    81825,
                    81814,
                    81815,
                    81816,
                    81817,
                    81818,
                    81819,
                    81820,
                    81821,
                    81874,
                    81875,
                    81876,
                    81877,
                    81886,
                    81887,
                    81888,
                    81889,
                    81878,
                    81879,
                    81880,
                    81881,
                    81882,
                    81883,
                    81884,
                    81885,
                    81890,
                    81891,
                    81892,
                    81893,
                    81902,
                    81903,
                    81904,
                    81905,
                    81894,
                    81895,
                    81896,
                    81897,
                    81898,
                    81899,
                    81900,
                    81901,
                    81906,
                    81907,
                    81908,
                    81909,
                    81918,
                    81919,
                    81920,
                    81921,
                    81910,
                    81911,
                    81912,
                    81913,
                    81914,
                    81915,
                    81916,
                    81917,
                    81962,
                    81963,
                    81964,
                    81965,
                    81974,
                    81975,
                    81976,
                    81977,
                    81966,
                    81967,
                    81968,
                    81969,
                    81970,
                    81971,
                    81972,
                    81973,
                    81826,
                    81827,
                    81828,
                    81829,
                    81838,
                    81839,
                    81840,
                    81841,
                    81830,
                    81831,
                    81832,
                    81833,
                    81834,
                    81835,
                    81836,
                    81837,
                    81842,
                    81843,
                    81844,
                    81845,
                    81854,
                    81855,
                    81856,
                    81857,
                    81846,
                    81847,
                    81848,
                    81849,
                    81850,
                    81851,
                    81852,
                    81853,
                    81858,
                    81859,
                    81860,
                    81861,
                    81870,
                    81871,
                    81872,
                    81873,
                    81862,
                    81863,
                    81864,
                    81865,
                    81866,
                    81867,
                    81868,
                    81869
                ],
                "placeholders": [
                    {
                        "position": "inside",
                        "images": [
                            {
                                "id": "63e7f5fbf08c3242e6859f58",
                                "name": "bday_0030_back.jpg",
                                "type": "image/jpeg",
                                "height": 3849,
                                "width": 2750,
                                "x": 0.7440094762474443,
                                "y": 0.4906514988405507,
                                "scale": 0.49589968099975856,
                                "angle": 0
                            },
                            {
                                "id": "63e7f5fbf08c3242e6859f58",
                                "name": "bday_0030_back.jpg",
                                "type": "image/jpeg",
                                "height": 3849,
                                "width": 2750,
                                "x": 0.24780487804878043,
                                "y": 0.4903646422579296,
                                "scale": 0.49560975609756086,
                                "angle": 0
                            }
                        ]
                    },
                    {
                        "position": "cover",
                        "images": [
                            {
                                "id": "63e7f5bb3ff59340bd57938f",
                                "name": "bday_0030_front.jpg",
                                "type": "image/jpeg",
                                "height": 3849,
                                "width": 2750,
                                "x": 0.7390939252654081,
                                "y": 0.49405654771100854,
                                "scale": 0.48716923114741456,
                                "angle": 0
                            }
                        ]
                    }
                ],
            }
        ]
    }
    new_product = CreateProduct.from_dict(new_product_data)
    print(api.create_product(7370017, new_product))
```


## Running Tests

`pipenv run pytest`