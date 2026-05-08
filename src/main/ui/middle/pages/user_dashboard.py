from src.main.ui.middle.pages.base_page import BasePage


class UserDashboard(BasePage):
    @property
    def welcome_text(self):
        return self.page.get_by_text("User Dashboard")

    @property
    def deposit_money_button(self):
        return self.page.get_by_role("button", name="Deposit Money")

    @property
    def deposit_money_heading(self):
        return self.page.get_by_role("heading", name="Deposit Money")

    @property
    def make_transfer_button(self):
        return self.page.get_by_role("button", name="Make a Transfer")

    @property
    def make_transfer_heading(self):
        return self.page.get_by_role("heading", name="Make a Transfer")

    @property
    def create_new_account_button(self):
        return self.page.get_by_role("button", name="➕ Create New Account")

    @property
    def account_selector(self):
        return self.page.locator(".account-selector")

    @property
    def deposit_amount_input(self):
        return self.page.get_by_placeholder("Enter amount")

    @property
    def deposit_submit_button(self):
        return self.page.get_by_role("button", name="Deposit")

    @property
    def recipient_name_input(self):
        return self.page.get_by_placeholder("Enter recipient name")

    @property
    def recipient_account_number_input(self):
        return self.page.get_by_placeholder("Enter recipient account number")

    @property
    def transfer_amount_input(self):
        return self.page.get_by_placeholder("Enter amount")

    @property
    def transfer_confirm_checkbox(self):
        return self.page.locator("#confirmCheck")

    @property
    def send_transfer_button(self):
        return self.page.get_by_role("button", name="Send Transfer")

    @property
    def user_info_button(self):
        return self.page.locator(".user-info")

    @property
    def edit_profile_text(self):
        return self.page.get_by_text("Edit Profile")

    @property
    def new_name_input(self):
        return self.page.get_by_placeholder("Enter new name")

    @property
    def save_changes_button(self):
        return self.page.get_by_role("button", name="Save Changes")

    @property
    def user_name_label(self):
        return self.page.locator(".user-name")

    def url(self):
        return "/dashboard"

    def create_new_account(self):
        self.create_new_account_button.click()
        return self

    def open_deposit_money(self):
        self.deposit_money_button.click()
        return self

    def select_account(self, account_id: str):
        self.account_selector.select_option(value=str(account_id))
        return self

    def fill_deposit_amount(self, amount: str):
        self.deposit_amount_input.fill(str(amount))
        return self

    def deposit(self):
        self.deposit_submit_button.click()
        return self

    def open_make_transfer(self):
        self.make_transfer_button.click()
        return self

    def fill_recipient_name(self, recipient_name: str):
        self.recipient_name_input.fill(recipient_name)
        return self

    def fill_recipient_account_number(self, account_number: str):
        self.recipient_account_number_input.fill(account_number)
        return self

    def fill_transfer_amount(self, amount: str):
        self.transfer_amount_input.fill(str(amount))
        return self

    def confirm_transfer(self):
        self.transfer_confirm_checkbox.check()
        return self

    def send_transfer(self):
        self.send_transfer_button.click()
        return self

    def open_edit_profile(self):
        self.user_info_button.click()
        return self

    def fill_new_name(self, name: str):
        self.new_name_input.fill(name)
        return self

    def save_profile_changes(self):
        self.save_changes_button.click()
        return self
