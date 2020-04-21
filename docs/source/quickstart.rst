.. _quickstart:

Quickstart Tutorial
===================

This tutorial guides you through how you can use ``statham`` to improve your use of external data sources, via an example app which gets and displays winners of a poll from an external API.

Suppose we are using an external Polls API which adheres to the following JSON Schema:

.. code-block:: json

    {
        "type": "object",
        "required": ["question", "choices"],
        "properties": {
            "question": {"type": "string"},
            "choices": {
                "type": "array",
                "items": {"$ref": "#/definitions/choice"}
            }
        },
        "definitions": {
            "choice": {
                "type": "object",
                "required": ["choice_text"],
                "properties": {
                    "choice_text": {
                        "type": "string", "maxLength": 200
                    },
                    "votes": {"type": "integer", "default": 0}
                }
            }
        }
    }

Our example app simply retrieves a Poll resource by ID and prints out the question, along with the winning choice:


.. code:: python

    import sys
    from typing import Dict

    import requests


    def get_poll(id: str) -> Dict:
        response = requests.get(f"http://api/poll/{id}")
        return response.json()

    def get_top_choice(poll: Dict) -> Dict:
        return sorted(
            poll["choices"],
            key=lambda choice: -choice.get("votes", 0),
        )[0]

    def display_poll(id: str):
        poll: Dict = get_poll(id)
        top_choice: Dict = get_top_choice(poll)
        print(f"""Question: {poll["question"]}
    Winner: {top_choice["choice_text"]}
    """
        )

    if __name__ == "__main__":
        display_poll(sys.argv[1])


Generating models
~~~~~~~~~~~~~~~~~

On the command-line, run

.. code-block:: bash

    $ statham --input schemas/poll.json --output app/poll.py

Then open up the ``app/poll.py``. You should see something like this:

.. code:: python

    from typing import List

    from statham.dsl.elements import Array, Integer, Object, String
    from statham.dsl.property import Property


    class Choice(Object):
        choice_text: str = Property(String(maxLength=200), required=True)
        votes: int = Property(Integer(default=0))


    class Poll(Object):
        question: str = Property(String(), required=True)
        choices: List[Choice] = Property(Array(Choice), required=True)


You can now import these generated models into your code to use as your representation of data described by the schema.


Using the models
~~~~~~~~~~~~~~~~

With the models added, our app now looks like this:

.. code:: python

    import requests

    from app.poll import Poll, Choice

    def get_poll(id: str) -> Poll:
        response = requests.get(f"http://api/poll/{id}")
        return Poll(response.json())

    def get_top_choice(poll: Poll) -> Choice:
        return sorted(poll.choices, key=lambda choice: -choice.votes)[0]

    def display_poll(id: str):
        poll: Poll = get_poll(id)
        top_choice: Choice = get_top_choice(poll)
        print(f"""Question: {poll.question}
    Winner: {top_choice.choice_text}
    """
        )

    if __name__ == "__main__":
        display_poll(sys.argv[1])


This looks similar, but we get the following improvements:

1. We will raise early with a specific validation error if we get bad data from the external source.
2. We no longer need to handle the default value for ``votes``.
3. We can now use mypy_ to check how we are using the data - if our original code accidentally had ``poll.get("voets", 0)``, it would fail silently. Now mypy_ will tell us if we try to access a bad attribute.


Extending the models
~~~~~~~~~~~~~~~~~~~~

.. _extending:

Now that we have models for the external data, we realise that some of our logic belongs there! The models can be easily extended with properties and methods.

.. code:: python

    from typing import List

    import requests

    from statham.dsl.elements import Array, Integer, Object, String
    from statham.dsl.property import Property


    class Choice(Object):
        choice_text: str = Property(String(maxLength=200), required=True)
        votes: int = Property(Integer(default=0))


    class Poll(Object):
        question: str = Property(String(maxLength=200), required=True)
        choices: List[Choice] = Property(Array(Choice), required=True)

        @classmethod
        def get(cls, id: str) -> "Poll":
            return cls(requests.get(f"http://api/poll/{id}").json())

        @property
        def top_choice(self) -> Choice:
            return sorted(self.choices, key=lambda choice: -choice.votes)[0]

        def __str__(self):
            return f"""Question: {self.question}
    Winner: {self.top_choice.choice_text}
    """


Now our app logic becomes as simple as this:

.. code:: python

    import sys

    from app.poll import Poll


    if __name__ == "__main__":
        print(str(Poll.get(sys.argv[1])))


.. note::

    When working with external schemas, it may be beneficial to preserve the generated models and extend them in sub-classes. This will help if you ever need to regenerate your models due to upsteam changes.

This concludes the quickstart tutorial, please see the rest of the documentation for more detailed information.

.. _mypy: http://mypy-lang.org/
