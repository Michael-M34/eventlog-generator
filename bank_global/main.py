from eventlog_environment import EventlogEnvironment
import random
import simpy

if __name__ == "__main__":
    bank_global_env = EventlogEnvironment()

    bank_global_env.add_step("Application Received", 10)
    bank_global_env.add_step("Application submitted to sales manager", 10)
    bank_global_env.add_step("Application scrutinised", 15)
    bank_global_env.add_step("Application returned", 5)
    bank_global_env.add_step("Application sent", 10)
    bank_global_env.add_step("Customer contacted", 30)
    bank_global_env.add_step("Collection notified of application", 5)
    bank_global_env.add_step("Application collected from customer", 4*60)
    bank_global_env.add_step("Customer details inputted", 15)
    bank_global_env.add_step("Application sent for credit assessment", 10)
    bank_global_env.add_step("Pre-screening performed", 10)
    bank_global_env.add_step("Credit assessment performed", 2*60)

    bank_global_env.add_step("Application investigated",5)
    bank_global_env.add_step("Application investigation complete", 1.5*60)
    bank_global_env.add_step("Application denied", 1)
    bank_global_env.add_step("Worksheet processed for verification",20)
    bank_global_env.add_step("CPV report received and attached",10)
    bank_global_env.add_step("Application checked", 30)
    bank_global_env.add_step("Clarification sought", 5)
    bank_global_env.add_step("Clarification received",10)
    bank_global_env.add_step("Application info cross verified", 15)
    bank_global_env.add_step("Penalisation processed",1)
    bank_global_env.add_step("Remaining application forwarded",10)
    bank_global_env.add_step("Credit card activated", 15)
    bank_global_env.add_step("Application archived",10)

    bank_global_env.add_step("DUD STEP", 100)

    bank_global_env.create_next_steps("Application Received", [("Application submitted to sales manager",0.5),("Application sent",0.5)])
    # bank_global_env.add_till_next_day_delay("NextDayDelay1", "Application Received", [], 9, 17)
    # bank_global_env.add_time_delay("Delay1", "NextDayDelay1", , 15)
    bank_global_env.create_next_steps("Application submitted to sales manager", [("Application scrutinised",1)])
    bank_global_env.create_next_steps("Application scrutinised", [("Application returned",0.5),("Application sent",0.5)])
    bank_global_env.create_next_steps("Customer contacted", [("Collection notified of application",1)])
    bank_global_env.create_next_steps("Collection notified of application", [("Application sent",1)])
    # bank_global_env.create_next_steps("Application sent", )
    bank_global_env.add_till_next_day_delay("TillNextDayDelay1", "Application sent", [("Customer details inputted",1)], 9, 17)
    bank_global_env.create_next_steps("Customer details inputted", [("Application returned",0.1),("Application sent for credit assessment",0.9)])
    bank_global_env.create_next_steps("Application sent for credit assessment", [("Pre-screening performed",1)])

    # bank_global_env.create_next_steps("Pre-screening performed", [("Credit assessment performed",0.5),("Application investigated",0.5)])
    bank_global_env.add_till_next_day_delay("TillNextDayDelay2", "Pre-screening performed", [("Credit assessment performed",0.95),("Application investigated",0.05)], 9, 17)
    bank_global_env.create_next_steps("Credit assessment performed", [("Application investigation complete",0.5),("Worksheet processed for verification",0.5)])

    bank_global_env.add_till_next_day_delay("TillNextDayDelay3", "DUD STEP", [], 9, 17)
    bank_global_env.add_till_next_day_delay("TillNextDayDelay4", "TillNextDayDelay3", [("Pre-screening performed",1)], 9, 17)

    bank_global_env.create_next_steps("Application investigated", [("Application denied",0.02),("TillNextDayDelay3",0.98)])
    bank_global_env.create_next_steps("Application investigation complete", [("Application denied",0.2),("TillNextDayDelay4",0.8)])


    # bank_global_env.create_next_steps("Worksheet processed for verification", [("CPV report received and attached",1)])

    bank_global_env.add_till_next_day_delay("TillNextDayDelay5", "Worksheet processed for verification", [], 9, 17)
    bank_global_env.add_time_delay("Delay1", "TillNextDayDelay5", [], 3*60)
    bank_global_env.add_till_next_day_delay("TillNextDayDelay6", "Delay1", [("CPV report received and attached",1)], 9, 17)


    # bank_global_env.create_next_steps("CPV report received and attached", [("Application checked",1)])
    bank_global_env.add_till_next_day_delay("TillNextDayDelay7", "CPV report received and attached", [("Application checked",1)], 9, 17)

    
    bank_global_env.create_next_steps("Application checked", [("Clarification sought",0.05),("Application info cross verified",0.95)])
    # bank_global_env.create_next_steps("Clarification sought", [("Clarification received",1)])

    bank_global_env.add_till_next_day_delay("TillNextDayDelay8", "Clarification sought", [("Clarification received",1)], 9, 17)

    bank_global_env.create_next_steps("Clarification received", [("Application checked",1)])
    # bank_global_env.create_next_steps("Application info cross verified", [("Remaining application forwarded",0.5)])
    bank_global_env.add_till_next_day_delay("TillNextDayDelay9", "Application info cross verified", [("Remaining application forwarded",1)], 9, 17)

    # bank_global_env.create_next_steps("Remaining application forwarded", [("Credit card activated",1)])
    bank_global_env.add_time_delay("Delay2", "Remaining application forwarded", [], 4*60)
    bank_global_env.add_till_next_day_delay("TillNextDayDelay10", "Delay2", [("Credit card activated",1)], 9, 17)

    bank_global_env.create_next_steps("Credit card activated", [("Application archived",1)])

    bank_global_env.add_eventlog_resource(7, 9, 17, ["Customer details inputted", "Pre-screening performed", "CPV report received and attached", "Credit card activated"], 60)


    orders = [i + 1 for i in range(100)]
    bank_global_env.complete_orders(orders, 60, [("Application Received", 0.8), ("Customer contacted", 0.2)])
