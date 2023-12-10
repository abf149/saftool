package saftool

import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}

/* "Efficient Processing" sparse representation format enum */
sealed trait SparseFormat
case object C extends SparseFormat
case object B extends SparseFormat
