# Green Stripe 76 buildroot package recipe (MOD Plugin Builder / Cloud Builder).
# The cloud builder accepts only this single .mk file, so the source must be
# fetched from a URL. Update _VERSION to the commit that should be built.
GREEN_STRIPE_76_VERSION = a79fbeadeccccea486f9611a3efb93e0bc17543b
GREEN_STRIPE_76_SITE_METHOD = git
GREEN_STRIPE_76_SITE = https://github.com/j4yj03/mod-1175-lv2.git
GREEN_STRIPE_76_LICENSE = MIT, ISC (LV2 ABI header)
GREEN_STRIPE_76_LICENSE_FILES = LICENSE
GREEN_STRIPE_76_DEPENDENCIES =
GREEN_STRIPE_76_BUNDLES = green-stripe-76.lv2
GREEN_STRIPE_76_TARGET_MAKE = $(TARGET_MAKE_ENV) $(TARGET_CONFIGURE_OPTS) $(MAKE) -C $(@D)

define GREEN_STRIPE_76_BUILD_CMDS
	$(GREEN_STRIPE_76_TARGET_MAKE) BUILD_DIR=build/mpb
endef

define GREEN_STRIPE_76_INSTALL_TARGET_CMDS
	$(GREEN_STRIPE_76_TARGET_MAKE) BUILD_DIR=build/mpb install DESTDIR=$(TARGET_DIR) PREFIX=/usr
endef

$(eval $(generic-package))
