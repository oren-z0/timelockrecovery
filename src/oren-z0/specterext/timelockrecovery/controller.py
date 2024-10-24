import logging
from flask import redirect, render_template, request, url_for, flash
from flask import current_app as app
from flask_login import login_required, current_user

from cryptoadvance.specter.specter import Specter
from cryptoadvance.specter.services.controller import user_secret_decrypted_required
from cryptoadvance.specter.user import User
from cryptoadvance.specter.wallet import Wallet
from .service import TimelockrecoveryService


logger = logging.getLogger(__name__)

timelockrecovery_endpoint = TimelockrecoveryService.blueprint

def ext() -> TimelockrecoveryService:
    ''' convenience for getting the extension-object'''
    return app.specter.ext["timelockrecovery"]

def specter() -> Specter:
    ''' convenience for getting the specter-object'''
    return app.specter


@timelockrecovery_endpoint.route("/")
@login_required
def index():
    return render_template(
        "timelockrecovery/index.jinja",
    )



@timelockrecovery_endpoint.route("/transactions")
@login_required
def transactions():
    # The wallet currently configured for ongoing autowithdrawals
    wallet: Wallet = TimelockrecoveryService.get_associated_wallet()

    return render_template(
        "timelockrecovery/transactions.jinja",
        wallet=wallet,
        services=app.specter.service_manager.services,
    )


@timelockrecovery_endpoint.route("/settings", methods=["GET"])
@login_required
def settings_get():
    associated_wallet: Wallet = TimelockrecoveryService.get_associated_wallet()

    # Get the user's Wallet objs, sorted by Wallet.name
    wallet_names = sorted(current_user.wallet_manager.wallets.keys())
    wallets = [current_user.wallet_manager.wallets[name] for name in wallet_names]

    return render_template(
        "timelockrecovery/settings.jinja",
        associated_wallet=associated_wallet,
        wallets=wallets,
        cookies=request.cookies,
    )

@timelockrecovery_endpoint.route("/settings", methods=["POST"])
@login_required
def settings_post():
    show_menu = request.form["show_menu"]
    user = app.specter.user_manager.get_user()
    if show_menu == "yes":
        user.add_service(TimelockrecoveryService.id)
    else:
        user.remove_service(TimelockrecoveryService.id)
    used_wallet_alias = request.form.get("used_wallet")
    if used_wallet_alias != None:
        wallet = current_user.wallet_manager.get_by_alias(used_wallet_alias)
        TimelockrecoveryService.set_associated_wallet(wallet)
    return redirect(url_for(f"{ TimelockrecoveryService.get_blueprint_name()}.settings_get"))