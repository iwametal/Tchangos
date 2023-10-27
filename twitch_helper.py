import requests

TWITCH_STREAM_API_ENDPOINT_V5 = "https://api.twitch.tv/helix/streams?user_login={}"
req = requests.Session()


class TwitchHelper:

    """"
    Function check_user:
    - Check if partner streamers are online

    :param user: name of stream user
    """
    @staticmethod
    def check_user(user, api_headers):
        try:
            url = TWITCH_STREAM_API_ENDPOINT_V5.format(user)
            try:
                resp = req.get(url, headers=api_headers)
                jsondata = resp.json()

                if jsondata.get('data')[0].get('user_login') == user:
                    return True

                return False
            except IndexError:
                return False

            except Exception as e:
                print("Error checking user: ", e)
                return False
        except Exception as e:
            print(e)
            return False