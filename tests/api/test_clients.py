import random

from django.urls import reverse, resolve

from backend.models import Client
from tests.handler import ViewTestCase
from model_bakery import baker


class ClientsAPIFetch(ViewTestCase):
    def test_clients_view_302_for_all_normal_get_requests(self):
        # All should be redirected as it should only accept from HTMX
        response = self.client.get(reverse("api:clients:fetch"))
        self.assertRedirects(response, "/login/?next=/api/clients/fetch", 302)
        self.login_user()
        response = self.client.get(reverse("api:clients:fetch"))
        self.assertRedirects(response, "/dashboard/clients/", 302)

    def test_clients_view_302_for_non_authenticated_users(self):
        response = self.client.get(reverse("api:clients:fetch"), **self.htmx_headers)
        self.assertEqual(response.status_code, 302)

    def test_clients_view_200_for_authenticated_users(self):
        self.login_user()
        response = self.client.get(reverse("api:clients:fetch"), **self.htmx_headers)
        self.assertEqual(response.status_code, 200)

    def test_clients_view_matches_with_urls_view(self):
        func = resolve("/api/clients/fetch").func
        func_name = f"{func.__module__}.{func.__name__}"
        self.assertEqual("/api/clients/fetch", reverse("api:clients:fetch"))
        self.assertEqual(
            "backend.api.clients.view.view_all.fetch_all_clients", func_name
        )

    def test_no_clients_get_returned_on_first(self):
        self.login_user()
        response = self.client.get(reverse("api:clients:fetch"), **self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context.get("clients")), 0)

    def test_clients_get_returned(self):
        self.login_user()

        random_amount_of_clients = random.randrange(2, 10)
        # Use baker to create random amount of  clients
        clients = baker.make(
            "backend.Client", _quantity=random_amount_of_clients, user=self.log_in_user
        )

        response = self.client.get(reverse("api:clients:fetch"), **self.htmx_headers)
        self.assertEqual(response.status_code, 200)

        # Check that the number of clients returned matches the number created
        self.assertEqual(len(response.context.get("clients")), random_amount_of_clients)

        # Check that all created clients are in the response
        for client in clients:
            self.assertIn(client, response.context.get("clients"))
