// See README.md for license details.

package saftool

import java.nio.file.{Paths, Files}
import java.nio.charset.StandardCharsets

import chisel3.stage.ChiselStage
import chisel3.Input
import chisel3.util._
//import chisel3.iotesters.{ChiselFlatSpec, Driver, PeekPokeTester}

import chisel3._
import chiseltest._
import org.scalatest.freespec.AnyFreeSpec
import chisel3.experimental.BundleLiterals._

import saftool._

class Test_Emit_Intersection extends AnyFreeSpec with ChiselScalatestTester {

  "Test_Emit_Intersection" in {
    test(new AUX_Intersect_Format_C_MDOrch_Uncoupled(16)) { dut =>

      var x=chisel3.getVerilogString(new AUX_Intersect_Format_C_MDOrch_Uncoupled(metaDataWidth = 8))
      print(x)
      Files.write(Paths.get("src/verilog/AUX_Intersect_Format_C_MDOrch_Uncoupled.v"), x.getBytes(StandardCharsets.UTF_8))

      x=chisel3.getVerilogString(new AUX_Intersect_Format_B_MDOrch_Uncoupled(mdTileSize = 8))
      print(x)
      Files.write(Paths.get("src/verilog/AUX_Intersect_Format_B_MDOrch_Uncoupled.v"), x.getBytes(StandardCharsets.UTF_8))

      x=chisel3.getVerilogString(new AUX_Intersect_Format_C_MDOrch_Coupled(metaDataWidth = 8))
      print(x)
      Files.write(Paths.get("src/verilog/AUX_Intersect_Format_C_MDOrch_Coupled.v"), x.getBytes(StandardCharsets.UTF_8))      

    }
  }
}
