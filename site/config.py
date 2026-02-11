# config.py - Applicaiton configuration and constants
# Copyright (C) 2026 Aaron Reichenbach
#
# This program is free software: you can redistribute it and/or modify         
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.



# -----------------------------------------------------------------------------
# Authorization Security
# -----------------------------------------------------------------------------

# Precalculated valid argon2 hash to force a call to verify() even when a user
# is not found.
DUMMY_HASH = '$argon2id$v=19$m=65536,t=3,p=4$ATQxgMcSIpT2cnBXT5jsSw$2Q9QgrVg2ym6jdS9IQjKSdLacqICyG4Y01TFn0ekrhg'

# Password policy configuration.
#   'safe-length' represents the length of a password that no longer needs to
#   meet other policy requirements for upper, lower, digit and symbol.
PASSWORD_POLICY = {
    'min-length': 12,
    'max-length': 64,
    'safe-length': 24, 
    'require-upper': True,
    'require-lower': True,
    'require-digit': True,
    'require-symbol': True
}

# Allowed symbols for passwords
PASSWORD_ALLOWED_SYMBOLS = "!@#$%^&*()[]{}_-+=,.?<>~|/"



# -----------------------------------------------------------------------------
# Application Globals
# -----------------------------------------------------------------------------

# Length of a username constraints.
USER_DETAIL_LIMITS = {
    'username-min-length': 3,
    'username-max-length': 64,
    'email-max-length': 100
}