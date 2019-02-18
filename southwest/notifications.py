class Notifications:
    @staticmethod
    def Phone(number):
        return {'mediaType': 'SMS', 'phoneNumber': number}

    @staticmethod
    def Email(email_address):
        return {'mediaType': 'EMAIL', 'emailAddress': email_address}
