def product_checker(trigger, order):
    if trigger.value.get("product_id") is None:
        return ValueError
    else:
        exist = False
        for product in order.products:
            if product.id == trigger.value.get("product_id"):
                exist = True
        return exist

def time_checker(trigger, order):
    if trigger.value.get("date_start") is None and trigger.value.get("date_end") is None:
        return ValueError
    else:
        today = time()
        # проверка вхождения по времени
        return trigger.value.get("date_start") <= today.date <= trigger.value.get("date_end")

db = {}
trigger_checkers = [product_checker, time_checker]


def check_actions(req, res):
    actions = db.loalty.actions.get()
    order = req.body()

    for action in order.actions:
        # Работа с payloads
        pass


    for action in actions:
        pass_checkers = True

        if not action.can_be_triggered:
            continue

        for trigger in action.triggers:
            if not pass_checkers:
                break

            for trigger_checker in trigger_checkers:
                result = trigger_checker(trigger, order)

                if result == ValueError:
                    continue
                elif result == False:
                    pass_checkers = False
                    break

        if pass_checkers:
            # Работа с payloads
            ...
        else:
            return res

