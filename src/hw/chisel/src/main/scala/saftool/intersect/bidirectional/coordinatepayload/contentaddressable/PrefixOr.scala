package saftool

import saftool._
import chisel3._
import chisel3.util._
import chisel3.experimental.ChiselEnum
import chisel3.util.Decoupled
import chisel3.util.{switch, is}

import chisel3._
import chisel3.util._

// Define a Bundle class for our circuit
class BitBundle(val bitLength: Int) extends Bundle {
  val bitstring = UInt(bitLength.W)
  val has_one = Bool()
}

class PrefixOR(val n: Int) extends Module with RequireSyncReset {
  require(isPow2(n), "Bitstring length must be a power of 2")

  val io = IO(new Bundle {
    val in = Input(UInt(n.W))
    val enable = Input(Bool())
    val out = Output(UInt(n.W))
  })

  // Function to process a pair of bundles and generate a new bundle
  def processPair(bundleA: BitBundle, bundleB: BitBundle): BitBundle = {
    val newBundleLength = bundleA.bitLength * 2
    val newBundle = Wire(new BitBundle(newBundleLength))
    when(bundleA.has_one) {
      newBundle.bitstring := Cat(bundleA.bitstring, Fill(bundleA.bitLength, 1.U))
      newBundle.has_one := true.B
    }.elsewhen(bundleB.has_one) {
      newBundle.bitstring := Cat(Fill(bundleB.bitLength, 0.U), bundleB.bitstring)
      newBundle.has_one := true.B
    }.otherwise {
      newBundle.bitstring := 0.U(newBundleLength.W)
      newBundle.has_one := false.B
    }
    newBundle
  }

  // Function to recursively process bundles
  def processBundles(bundles: Seq[BitBundle], level: Int): BitBundle = {
    if (level == 0) {
      bundles.head
    } else {
      val pairedBundles = bundles.grouped(2).map {
        case Seq(a, b) => processPair(a, b)
      }.toSeq
      processBundles(pairedBundles, level - 1)
    }
  }

  // Initialize bundles from the input bitstring
  val initialBundles = Seq.tabulate(n)(i => {
    val bundle = Wire(new BitBundle(1))
    bundle.bitstring := io.in(i)
    bundle.has_one := io.in(i) === 1.U
    bundle
  })

  // Process bundles recursively
  val finalBundle = processBundles(initialBundles, log2Ceil(n))

  // Generate output
  io.out := Mux(io.enable, finalBundle.bitstring, 0.U)
}
