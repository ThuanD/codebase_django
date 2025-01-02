import unittest

from apps.api_doc.docs import RequestBodyValidationErrorExample

from app.django.exception import RequestBodyValidationError


class TestRequestBodyValidationErrorExample(unittest.TestCase):
    """Test suite for RequestBodyValidationErrorExample."""

    def test_request_body_validation_error_example(self) -> None:
        """Test the initialization of RequestBodyValidationErrorExample."""
        example = RequestBodyValidationErrorExample()

        self.assertEqual(example.name, "RequestBodyValidationError")
        self.assertEqual(
            example.description,
            "Check the request body schema to see the validation information "
            "for the fields. Error `message` are mutable.",
        )

        expected_value = RequestBodyValidationError(
            {
                "field": [
                    {
                        "message": "Error message for this field!",
                        "code": "invalid",
                    }
                ]
            }
        ).get_full_details()

        self.assertEqual(example.value, expected_value)
