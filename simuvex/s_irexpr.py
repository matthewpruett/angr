#!/usr/bin/env python
'''This module handles constraint generation.'''

import z3
import s_irop
import s_ccall
import logging
import s_helpers

l = logging.getLogger("s_irexpr")
#l.setLevel(logging.DEBUG)

class UnsupportedIRExprType(Exception):
	pass

class SimIRExpr:
	def __init__(self, expr, state):
		self.state = state

		func_name = "symbolic_" + type(expr).__name__
		l.debug("Looking for handler %s for IRExpr %s" % (func_name, type(expr).__name__))
		if hasattr(self, func_name):
			self.expr, self.constraints = getattr(self, func_name)(expr)
		else:
			raise UnsupportedIRExprType("Unsupported expression type %s." % type(expr))

	def expr_and_constraints(self):
		return self.expr, self.constraints

	###########################
	### Expression handlers ###
	###########################

	# TODO: make sure the way we're handling reads of parts of registers is correct
	def symbolic_Get(self, expr):
		# TODO: proper SSO registers
		size = s_helpers.get_size(expr.type)
		offset_vec = z3.BitVecVal(expr.offset, self.state.arch.bits)
		reg_expr, get_constraints = self.state.registers.load(offset_vec, size)
		return reg_expr, get_constraints
	
	def symbolic_op(self, expr):
		args = expr.args()
		return s_irop.translate(expr.op, args, self.state)
	symbolic_Unop = symbolic_op
	symbolic_Binop = symbolic_op
	symbolic_Triop = symbolic_op
	symbolic_Qop = symbolic_op
	
	def symbolic_RdTmp(self, expr):
		return self.state.temps[expr.tmp], [ ]
	
	def symbolic_Const(self, expr):
		return s_helpers.translate_irconst(expr.con), [ ]
	
	def symbolic_Load(self, expr):
		size = s_helpers.get_size(expr.type)
		addr, addr_constraints = SimIRExpr(expr.addr, self.state).expr_and_constraints()
		mem_expr, load_constraints = self.state.memory.load(addr, size, self.state.old_constraints + addr_constraints)
		mem_expr = s_helpers.fix_endian(expr.endness, mem_expr)
	
		l.debug("Load of size %d got size %d" % (size, mem_expr.size()))
		return mem_expr, load_constraints + addr_constraints
	
	def symbolic_CCall(self, expr):
		s_args, s_constraints = zip(*[ SimIRExpr(a, self.state).expr_and_constraints() for a in expr.args() ])
		s_constraints = sum(s_constraints[0], [])
		if hasattr(s_ccall, expr.callee.name):
			func = getattr(s_ccall, expr.callee.name)
			retval, retval_constraints = func(self.state, *s_args)
			return retval, s_constraints + retval_constraints
	
		raise Exception("Unsupported callee %s" % expr.callee.name)
	
	def symbolic_Mux0X(self, expr):
		cond, cond_constraints =   SimIRExpr(expr.cond, self.state).expr_and_constraints()
		expr0, expr0_constraints = SimIRExpr(expr.expr0, self.state).expr_and_constraints()
		exprX, exprX_constraints = SimIRExpr(expr.exprX, self.state).expr_and_constraints()
	
		cond0_constraints = z3.And(*[[ cond == 0 ] + expr0_constraints ])
		condX_constraints = z3.And(*[[ cond != 0 ] + exprX_constraints ])
		return z3.If(cond == 0, expr0, exprX), [ z3.Or(cond0_constraints, condX_constraints) ]
