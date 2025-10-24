fof(f1, axiom, ?[X]: (examine_thoroughly(X))).
fof(f2, axiom, ![X]: ((examine_thoroughly(X))) => ?[X]: ( (examine_casually(X)) )).
fof(f3, axiom, ?[X]: (reject_request(X))).
fof(f4, axiom, ![X]: ((check_ticket(X)) | (reinitiate_request(X))) => ?[X]: ( (reject_request(X)) | (pay_compensation(X)) )).
fof(f5, axiom, ![X]: ~(((register_request(X))) & ((reject_request(X)) | (pay_compensation(X))))).
fof(f6, axiom, ![X]: ~(((check_ticket(X)) | (decide(X))) & ((reinitiate_request(X))))).
fof(f7, axiom, ![X]: ((check_ticket(X)) | (decide(X))) => ?[X]: ( (reinitiate_request(X)) )).
fof(f8, axiom, ![X]: ((register_request(X))) => ?[X]: ( (check_ticket(X)) | (reinitiate_request(X)) )).
fof(f9, axiom, ?[X]: (check_ticket(X)) | (examine_casually(X))).
fof(f10, axiom, ![X]: ~(((examine_thoroughly(X))) & ((examine_casually(X))))).
fof(f11, axiom, ![X]: ((reject_request(X))) => ?[X]: ( (pay_compensation(X)) )).
fof(f12, axiom, ![X]: ((check_ticket(X)) | (examine_casually(X))) => ?[X]: ( (decide(X)) )).
fof(f13, axiom, ?[X]: (check_ticket(X))).
fof(f14, axiom, ![X]: ~(((check_ticket(X)) | (examine_casually(X))) & ((decide(X))))).
fof(f15, axiom, ?[X]: (register_request(X))).
fof(f16, axiom, ![X]: ((check_ticket(X))) => ?[X]: ( (examine_thoroughly(X)) | (examine_casually(X)) )).
fof(f17, axiom, ![X]: ~(((register_request(X))) & ((check_ticket(X)) | (reinitiate_request(X))))).
fof(f18, axiom, ![X]: ~(((reject_request(X))) & ((pay_compensation(X))))).
fof(f19, axiom, ?[X]: (check_ticket(X)) | (decide(X))).
fof(f20, axiom, ![X]: ~(((check_ticket(X)) | (reinitiate_request(X))) & ((reject_request(X)) | (pay_compensation(X))))).
fof(f21, axiom, ![X]: ~(((check_ticket(X))) & ((examine_thoroughly(X)) | (examine_casually(X))))).