from discord.ext import commands

command_error_list = {
	'check-failure': {
          'error': commands.CheckFailure,
		  'prefix': '❌ | '
	},
	'command-on-cooldown': {
          'error': commands.CommandOnCooldown,
		  'prefix': '💔 | '
	},
	'missing-permissions': {
          'error': commands.MissingPermissions,
		  'prefix': '🚫 | '
	},
	'missing-required-argument': {
          'error': commands.MissingRequiredArgument,
          'prefix': '⚠️ | '
	},
}
